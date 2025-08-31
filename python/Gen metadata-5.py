import tkinter as tk
from tkinter import colorchooser, messagebox, simpledialog, Toplevel, Text, Scrollbar, END, INSERT
import re # Importation nécessaire pour les expressions régulières

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Générateur de Métadonnées Multicraft (Luanti)")
        self.root.geometry("800x450")
        self.root.resizable(False, False)

        # Variables d'état
        self.item_name = tk.StringVar(value="default:stone")
        self.amount = tk.IntVar(value=1)
        self.description_content = ""
        self.short_description_content = ""
        self.item_color_hex = ""

        self._create_widgets()
        self._update_command_display()

    def _create_widgets(self):
        # Section Entrée Item
        item_frame = tk.LabelFrame(self.root, text="Informations sur l'objet", padx=10, pady=10)
        item_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(item_frame, text="Nom de l'objet (ex: default:stone):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        item_entry = tk.Entry(item_frame, textvariable=self.item_name, width=40)
        item_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        item_entry.bind("<KeyRelease>", self._on_input_change)

        tk.Label(item_frame, text="Quantité:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        amount_entry = tk.Entry(item_frame, textvariable=self.amount, width=10)
        amount_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        amount_entry.bind("<KeyRelease>", self._on_input_change)

        # Section Boutons de Métadonnées
        metadata_buttons_frame = tk.LabelFrame(self.root, text="Métadonnées", padx=10, pady=10)
        metadata_buttons_frame.pack(pady=10, padx=10, fill="x")

        btn_desc = tk.Button(metadata_buttons_frame, text="Modifier Description", command=self._open_description_editor)
        btn_desc.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        btn_short_desc = tk.Button(metadata_buttons_frame, text="Modifier Description Courte", command=self._open_short_description_editor)
        btn_short_desc.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        btn_item_color = tk.Button(metadata_buttons_frame, text="Modifier Couleur de l'Item", command=self._open_item_color_picker)
        btn_item_color.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Section Affichage de la Commande
        command_frame = tk.LabelFrame(self.root, text="Commande Générée", padx=10, pady=10)
        command_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.command_display = Text(command_frame, wrap="word", height=5, state="disabled", bg="lightgray", font=("Courier", 10))
        self.command_display.pack(fill="both", expand=True, padx=5, pady=5)

        # Bouton Copier
        copy_button = tk.Button(self.root, text="Copier la Commande", command=self._copy_command)
        copy_button.pack(pady=10)

    def _on_input_change(self, event=None):
        self._update_command_display()

    def _update_command_display(self):
        item_name = self.item_name.get()
        amount = self.amount.get()

        metadata_string = ""
        
        # Flag pour savoir si des métadonnées standard (description/short_description) sont présentes
        has_standard_metadata_content = False

        if self.description_content:
            metadata_string += f"\\u0003description\\u0002{self.description_content}"
            has_standard_metadata_content = True
        
        if self.short_description_content:
            metadata_string += f"\\u0003short_description\\u0002{self.short_description_content}"
            has_standard_metadata_content = True
        
        # Ajout de la couleur de l'item
        if self.item_color_hex:
            # La métadonnée de couleur inclut son propre \u0003 final
            metadata_string += f"\\u001bE\\u0003color\\u0002{self.item_color_hex}\\u0003"
        elif has_standard_metadata_content:
            # Si il y a des métadonnées standard MAIS PAS de couleur d'item,
            # alors on ajoute le \u0003 final pour terminer la chaîne de métadonnées standard.
            metadata_string += "\\u0003"

        # La commande finale
        command = f"/giveme {item_name} {amount} 0 \"{metadata_string}\""

        self.command_display.config(state="normal")
        self.command_display.delete(1.0, END)
        self.command_display.insert(END, command)
        self.command_display.config(state="disabled")

    def _open_description_editor(self):
        self._open_text_editor("Modifier Description de l'Item", self.description_content, self._set_description_content)

    def _open_short_description_editor(self):
        self._open_text_editor("Modifier Description Courte de l'Item", self.short_description_content, self._set_short_description_content)

    def _open_text_editor(self, title, initial_text, set_content_callback):
        editor_window = Toplevel(self.root)
        editor_window.title(title)
        editor_window.geometry("600x400")
        editor_window.transient(self.root) # Rend la fenêtre modale par rapport à la fenêtre principale
        editor_window.grab_set() # Empêche l'interaction avec la fenêtre principale

        # Champ de texte
        text_frame = tk.Frame(editor_window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)

        text_editor = Text(text_frame, wrap="word", font=("Arial", 10))
        text_editor.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(text_frame, command=text_editor.yview)
        scrollbar.pack(side="right", fill="y")
        text_editor.config(yscrollcommand=scrollbar.set)

        # Fonction pour appliquer le formatage en direct
        def _apply_formatting(event=None):
            # Supprimer toutes les balises de couleur existantes
            for tag in text_editor.tag_names():
                if tag.startswith("color_"):
                    text_editor.tag_delete(tag)
            
            # Obtenir le contenu actuel
            content_for_display = text_editor.get(1.0, END)
            
            # Expression régulière pour trouver les codes de couleur et capturer la valeur hexadécimale
            color_pattern = r"(\\u001b\(c@#([0-9a-fA-F]{6})\))"
            
            last_end_index = "1.0"
            current_color = None

            # Trouver tous les codes de couleur et appliquer le formatage
            for match in re.finditer(color_pattern, content_for_display):
                full_code = match.group(1) # Le code de couleur complet (ex: \u001b(c@#FF0000))
                hex_color = "#" + match.group(2) # La couleur hexadécimale (ex: #FF0000)
                
                start_index = text_editor.index(f"1.0 + {match.start()}c")
                end_index = text_editor.index(f"1.0 + {match.end()}c")
                
                # Appliquer la couleur précédente au segment de texte avant le code actuel
                if current_color:
                    text_editor.tag_add(f"color_{current_color}", last_end_index, start_index)
                    text_editor.tag_config(f"color_{current_color}", foreground=current_color)
                
                # Mettre à jour la couleur actuelle pour le texte *après* ce code
                current_color = hex_color
                last_end_index = end_index # Commencer à appliquer la nouvelle couleur à partir d'ici

            # Appliquer la dernière couleur au texte restant
            if current_color:
                text_editor.tag_add(f"color_{current_color}", last_end_index, END)
                text_editor.tag_config(f"color_{current_color}", foreground=current_color)

        # Boutons de l'éditeur
        button_frame = tk.Frame(editor_window, padx=10, pady=10)
        button_frame.pack(fill="x")

        def insert_color_code():
            color_code = colorchooser.askcolor()[1] # Retourne (rgb_tuple, hex_code)
            if color_code:
                # Insérer la séquence de couleur au curseur
                text_editor.insert(INSERT, f"\\u001b(c@{color_code})")
                _apply_formatting() # Appliquer le formatage immédiatement après l'insertion

        def confirm_text():
            # Get the content from the Text widget, excluding the implicit trailing newline.
            raw_content = text_editor.get(1.0, "end-1c")
            # Replace actual newlines with the escaped newline sequence for Luanti
            processed_content = raw_content.replace("\n", "\\n")
            # No need for strip() here, as "end-1c" already handles the trailing newline
            set_content_callback(processed_content)
            editor_window.destroy()
            editor_window.grab_release() # Relâche le focus sur la fenêtre principale
            self._update_command_display()

        btn_insert_color = tk.Button(button_frame, text="Insérer Code Couleur", command=insert_color_code)
        btn_insert_color.pack(side="left", padx=5)
        
        btn_confirm = tk.Button(button_frame, text="Confirmer", command=confirm_text)
        btn_confirm.pack(side="right", padx=5)

        # Bind pour chaque frappe de touche et clic de souris pour mettre à jour le formatage
        text_editor.bind("<KeyRelease>", _apply_formatting)
        text_editor.bind("<ButtonRelease-1>", _apply_formatting)

        # Appliquer le formatage initialement quand l'éditeur s'ouvre
        # Remplacer les \n par de vrais retours à la ligne pour l'affichage
        display_text = initial_text.replace("\\n", "\n")
        text_editor.delete(1.0, END)
        text_editor.insert(END, display_text)
        _apply_formatting() # Appliquer le formatage après l'insertion du texte


        # Gérer la fermeture de la fenêtre
        editor_window.protocol("WM_DELETE_WINDOW", lambda: (editor_window.destroy(), editor_window.grab_release()))


    def _set_description_content(self, content):
        self.description_content = content

    def _set_short_description_content(self, content):
        self.short_description_content = content

    def _open_item_color_picker(self):
        color_window = Toplevel(self.root)
        color_window.title("Choisir Couleur de l'Item")
        color_window.geometry("300x180") # Increased height to accommodate new button
        color_window.transient(self.root)
        color_window.grab_set()

        chosen_color = tk.StringVar(value=self.item_color_hex if self.item_color_hex else "#FFFFFF") # Default to white

        def pick_color():
            color_code = colorchooser.askcolor(color=chosen_color.get())[1]
            if color_code:
                chosen_color.set(color_code)
                color_display_label.config(bg=color_code)

        def confirm_color():
            self.item_color_hex = chosen_color.get()
            color_window.destroy()
            color_window.grab_release()
            self._update_command_display()

        def cancel_color():
            self.item_color_hex = "" # Clear the item color
            color_window.destroy()
            color_window.grab_release()
            self._update_command_display()

        tk.Label(color_window, text="Couleur sélectionnée:").pack(pady=5)
        color_display_label = tk.Label(color_window, bg=chosen_color.get(), width=10, height=2, relief="sunken")
        color_display_label.pack(pady=5)

        btn_pick = tk.Button(color_window, text="Choisir une Couleur", command=pick_color)
        btn_pick.pack(pady=5)

        btn_confirm = tk.Button(color_window, text="Confirmer", command=confirm_color)
        btn_confirm.pack(pady=5)
        
        # New Cancel button
        btn_cancel = tk.Button(color_window, text="enlever la couleur", command=cancel_color)
        btn_cancel.pack(pady=5)
        
        # Gérer la fermeture de la fenêtre
        color_window.protocol("WM_DELETE_WINDOW", lambda: (color_window.destroy(), color_window.grab_release()))


    def _copy_command(self):
        command_text = self.command_display.get(1.0, END).strip()
        if self.root.clipboard_clear: # Check if clipboard_clear exists (may not on all systems)
            self.root.clipboard_clear()
        self.root.clipboard_append(command_text)
        messagebox.showinfo("Copié !", "La commande a été copiée dans le presse-papiers.")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
