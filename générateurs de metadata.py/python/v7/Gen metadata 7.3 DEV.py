import tkinter as tk
from tkinter import colorchooser, messagebox, Toplevel, Text, Scrollbar, END, INSERT
import re
import json # Importation nécessaire pour gérer les données JSON des capacités de l'outil

# Valeurs par défaut pour les capacités de l'outil, sous forme de dictionnaire Python
DEFAULT_TOOL_CAPS_DICT = {
    "damage_groups": {"fleshy": 1.0},
    "full_punch_interval": 0.5,
    "groupcaps": {
        "cracky": {"maxlevel": 3, "times": [None, 1.0, 1.0, 1.0], "uses": 100},
        "choppy": {"maxlevel": 1, "times": [None, 1.0, 1.0, 1.0], "uses": 100},
        "crumbly": {"maxlevel": 3, "times": [None, 1.0, 1.0, 1.0], "uses": 100},
        "snappy": {"maxlevel": 3, "times": [None, 1.0, 1.0, 1.0], "uses": 100}
    },
    "max_drop_level": 1
}

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Verssion 7.3 DEV generateur de metadata")
        self.root.geometry("800x450")
        self.root.resizable(False, False)

        # Variables d'état
        self.item_name = tk.StringVar(value="default:stone")
        self.amount = tk.IntVar(value=1)
        self.description_content = ""
        self.short_description_content = ""
        self.item_color_hex = ""
        # Données pour les capacités de l'outil, initialisées à None.
        # Elles ne seront incluses dans la commande que si l'utilisateur les modifie et confirme.
        self.tool_capabilities_data = None 

        self._create_widgets()
        self._update_command_display()

    def _create_widgets(self):
        # Section Entrée Item
        item_frame = tk.LabelFrame(self.root, text="informations de base", padx=10, pady=10)
        item_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(item_frame, text="Nom de l'objet (ex: default:stone):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        item_entry = tk.Entry(item_frame, textvariable=self.item_name, width=40)
        item_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        item_entry.bind("<KeyRelease>", self._on_input_change)

        tk.Label(item_frame, text="Qtt:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        amount_entry = tk.Entry(item_frame, textvariable=self.amount, width=10)
        amount_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        amount_entry.bind("<KeyRelease>", self._on_input_change)

        # Section Boutons de Métadonnées
        metadata_buttons_frame = tk.LabelFrame(self.root, text="Métadonnées", padx=10, pady=10)
        metadata_buttons_frame.pack(pady=10, padx=10, fill="x")

        # Nouveau bouton pour les capacités de l'outil
        btn_tool_caps = tk.Button(metadata_buttons_frame, text="Capacités de l'outil", command=self._open_tool_capabilities_editor)
        btn_tool_caps.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        btn_desc = tk.Button(metadata_buttons_frame, text="Modifier Description", command=self._open_description_editor)
        btn_desc.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        btn_short_desc = tk.Button(metadata_buttons_frame, text="Modifier Description Courte", command=self._open_short_description_editor)
        btn_short_desc.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        btn_item_color = tk.Button(metadata_buttons_frame, text="Modifier Couleur de l'Item", command=self._open_item_color_picker)
        btn_item_color.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # Section Affichage de la Commande
        command_frame = tk.LabelFrame(self.root, text="Commande Générée", padx=10, pady=10)
        command_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.command_display = Text(command_frame, wrap="word", height=5, state="disabled", bg="lightgray", font=("Courier", 10))
        self.command_display.pack(fill="both", expand=True, padx=5, pady=5)

        # Boutons de contrôle de la commande
        command_control_frame = tk.Frame(self.root)
        command_control_frame.pack(pady=5)

        copy_button = tk.Button(command_control_frame, text="Copier la Commande", command=self._copy_command)
        copy_button.pack(side="left", padx=5)

        # Nouveau bouton Actualiser
        refresh_button = tk.Button(command_control_frame, text="Actualiser la Commande", command=self._update_command_display)
        refresh_button.pack(side="left", padx=5)

    def _on_input_change(self, event=None):
        self._update_command_display()

    def _update_command_display(self):
        item_name = self.item_name.get()
        amount = self.amount.get()

        standard_metadata_parts = [] # List to hold parts like "key\u0002value"
        item_color_block = ""
        
        # 1. Tool Capabilities (first priority, handled if self.tool_capabilities_data is not None)
        if self.tool_capabilities_data is not None:
            # Convert Python dict to JSON string, ensuring no extra spaces for compactness, then escape quotes
            tool_caps_json_raw = json.dumps(self.tool_capabilities_data, separators=(',', ':'))
            tool_caps_json_escaped = tool_caps_json_raw.replace('"', '\\"')
            standard_metadata_parts.append(f"tool_capabilities\\u0002{tool_caps_json_escaped}")

        # 2. Description
        if self.description_content:
            standard_metadata_parts.append(f"description\\u0002{self.description_content}")

        # 3. Short Description
        if self.short_description_content:
            standard_metadata_parts.append(f"short_description\\u0002{self.short_description_content}")

        # Construct the main metadata string with \u0003 separators and the x_enchanting prefix
        final_metadata_string_core = ""
        if standard_metadata_parts:
            # Add the global prefix for x_enchanting if any standard metadata block is present
            final_metadata_string_core += "\\u0001x_enchanting\\u0002"
            # Join the blocks with \u0003 and add a final \u0003
            final_metadata_string_core += "\\u0003" + "\\u0003".join(standard_metadata_parts) + "\\u0003"

        # 4. Item Color (special handling, always appended at the end)
        if self.item_color_hex:
            item_color_block = f"\\u001bE\\u0003color\\u0002{self.item_color_hex}\\u0003"
        
        # Combine core metadata and item color
        final_metadata_string = final_metadata_string_core + item_color_block

        # La commande finale
        command = f"/giveme {item_name} {amount} 0 \"{final_metadata_string}\""

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
        editor_window.transient(self.root)
        editor_window.grab_set()

        text_frame = tk.Frame(editor_window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)

        text_editor = Text(text_frame, wrap="word", font=("Arial", 10))
        text_editor.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(text_frame, command=text_editor.yview)
        scrollbar.pack(side="right", fill="y")
        text_editor.config(yscrollcommand=scrollbar.set)

        editor_window.show_codes = True 

        def _apply_formatting(event=None):
            cursor_pos = text_editor.index(INSERT)

            for tag in text_editor.tag_names():
                if tag.startswith("color_") or tag == "hidden_code_tag" or tag == "visible_code_tag" or tag == "default_color":
                    text_editor.tag_delete(tag)
            
            content_in_editor = text_editor.get(1.0, END)
            color_pattern = r"(\\u001b\(c@#([0-9a-fA-F]{6})\))"
            
            last_processed_index = "1.0"
            current_color = "black"

            for match in re.finditer(color_pattern, content_in_editor):
                full_code = match.group(1)
                hex_color = "#" + match.group(2)
                
                code_start_index = text_editor.index(f"1.0 + {match.start()}c")
                code_end_index = text_editor.index(f"1.0 + {match.end()}c")
                
                if text_editor.compare(last_processed_index, "<", code_start_index):
                    text_editor.tag_add(f"color_{current_color}", last_processed_index, code_start_index)
                    text_editor.tag_config(f"color_{current_color}", foreground=current_color)
                
                if not editor_window.show_codes:
                    text_editor.tag_add("hidden_code_tag", code_start_index, code_end_index)
                    text_editor.tag_config("hidden_code_tag", foreground=text_editor.cget("bg"), background=text_editor.cget("bg"), font=("Arial", 1))
                else:
                    text_editor.tag_add("visible_code_tag", code_start_index, code_end_index)
                    text_editor.tag_config("visible_code_tag", foreground="black", background=text_editor.cget("bg"), font=("Arial", 10))

                current_color = hex_color
                last_processed_index = code_end_index

            if text_editor.compare(last_processed_index, "<", END):
                text_editor.tag_add(f"color_{current_color}", last_processed_index, END)
                text_editor.tag_config(f"color_{current_color}", foreground=current_color)
            
            try:
                text_editor.mark_set(INSERT, cursor_pos)
                text_editor.see(INSERT)
            except tk.TclError:
                text_editor.mark_set(INSERT, END)


        button_frame = tk.Frame(editor_window, padx=10, pady=10)
        button_frame.pack(fill="x")

        def insert_color_code():
            color_code = colorchooser.askcolor()[1]
            if color_code:
                text_editor.insert(INSERT, f"\\u001b(c@{color_code})")
                _apply_formatting()

        def confirm_text():
            raw_content = text_editor.get(1.0, "end-1c")
            processed_content = raw_content.replace("\n", "\\n")
            set_content_callback(processed_content)
            editor_window.destroy()
            editor_window.grab_release()

        def toggle_code_visibility():
            editor_window.show_codes = not editor_window.show_codes
            if editor_window.show_codes:
                toggle_button.config(text="Masquer Codes")
            else:
                toggle_button.config(text="Afficher Codes")
            _apply_formatting()

        btn_insert_color = tk.Button(button_frame, text="Insérer Code Couleur", command=insert_color_code)
        btn_insert_color.pack(side="left", padx=5)
        
        toggle_button = tk.Button(button_frame, text="Masquer Codes" if editor_window.show_codes else "Afficher Codes", command=toggle_code_visibility)
        toggle_button.pack(side="left", padx=5)

        btn_confirm = tk.Button(button_frame, text="Confirmer", command=confirm_text)
        btn_confirm.pack(side="right", padx=5)

        text_editor.bind("<KeyRelease>", _apply_formatting)
        text_editor.bind("<ButtonRelease-1>", _apply_formatting)

        display_text = initial_text.replace("\\n", "\n")
        text_editor.delete(1.0, END)
        text_editor.insert(END, display_text)
        _apply_formatting()

        editor_window.protocol("WM_DELETE_WINDOW", lambda: (editor_window.destroy(), editor_window.grab_release()))

    def _set_description_content(self, content):
        self.description_content = content

    def _set_short_description_content(self, content):
        self.short_description_content = content

    def _open_item_color_picker(self):
        color_window = Toplevel(self.root)
        color_window.title("Choisir Couleur de l'Item")
        color_window.geometry("300x200")
        color_window.transient(self.root)
        color_window.grab_set()

        chosen_color = tk.StringVar(value=self.item_color_hex if self.item_color_hex else "#FFFFFF")

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
            self.item_color_hex = ""
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
        
        btn_cancel = tk.Button(color_window, text="Annuler la Couleur", command=cancel_color)
        btn_cancel.pack(pady=5)
        
        color_window.protocol("WM_DELETE_WINDOW", lambda: (color_window.destroy(), color_window.grab_release()))


    def _copy_command(self):
        command_text = self.command_display.get(1.0, END).strip()
        if self.root.clipboard_clear:
            self.root.clipboard_clear()
        self.root.clipboard_append(command_text)
        messagebox.showinfo("Copié !", "La commande a été copiée dans le presse-papiers.")

    # --- Nouvelle fonction pour l'éditeur de capacités de l'outil ---
    def _open_tool_capabilities_editor(self):
        editor_window = Toplevel(self.root)
        editor_window.title("Modifier Capacités de l'Outil")
        editor_window.geometry("600x700") # Taille ajustée pour plus de champs
        editor_window.transient(self.root)
        editor_window.grab_set()

        # Initialiser les variables Tkinter avec les données actuelles (si elles existent) ou les valeurs par défaut
        # Utiliser une copie profonde pour éviter de modifier le dictionnaire original avant confirmation
        current_data_for_editor = self.tool_capabilities_data if self.tool_capabilities_data is not None else DEFAULT_TOOL_CAPS_DICT.copy()

        # Variables pour les dégâts aux entités
        self.fleshy_damage_var = tk.DoubleVar(value=current_data_for_editor["damage_groups"].get("fleshy", 1.0))
        self.full_punch_interval_var = tk.DoubleVar(value=current_data_for_editor.get("full_punch_interval", 0.5))

        # Variables pour le cassage des blocs
        self.groupcaps_vars = {}
        for group in ["cracky", "choppy", "crumbly", "snappy"]:
            self.groupcaps_vars[group] = {
                "maxlevel": tk.IntVar(value=current_data_for_editor["groupcaps"].get(group, {}).get("maxlevel", 3)),
                "times": [
                    tk.StringVar(value="null"), # Le premier est toujours null
                    tk.DoubleVar(value=current_data_for_editor["groupcaps"].get(group, {}).get("times", [None, 1.0, 1.0, 1.0])[1]),
                    tk.DoubleVar(value=current_data_for_editor["groupcaps"].get(group, {}).get("times", [None, 1.0, 1.0, 1.0])[2]),
                    tk.DoubleVar(value=current_data_for_editor["groupcaps"].get(group, {}).get("times", [None, 1.0, 1.0, 1.0])[3])
                ],
                "uses": tk.IntVar(value=current_data_for_editor["groupcaps"].get(group, {}).get("uses", 100))
            }
        
        # max_drop_level (fixe pour l'instant, non éditable dans l'UI)
        self.max_drop_level_var = tk.IntVar(value=current_data_for_editor.get("max_drop_level", 1))

        # Cadre principal pour le scroll
        main_frame = tk.Frame(editor_window)
        main_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(main_frame)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


        # --- Catégorie Arme ---
        weapon_frame = tk.LabelFrame(scrollable_frame, text="Arme", padx=10, pady=10)
        weapon_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(weapon_frame, text="Dégâts infligés (fleshy):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        tk.Entry(weapon_frame, textvariable=self.fleshy_damage_var).grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        tk.Label(weapon_frame, text="Vitesse de frappe (full_punch_interval):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        tk.Entry(weapon_frame, textvariable=self.full_punch_interval_var).grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        # --- Catégorie Outil ---
        tool_frame = tk.LabelFrame(scrollable_frame, text="Outil", padx=10, pady=10)
        tool_frame.pack(pady=10, padx=10, fill="x")

        for i, group in enumerate(["cracky", "choppy", "crumbly", "snappy"]):
            group_frame = tk.LabelFrame(tool_frame, text=f"{group.capitalize()}", padx=5, pady=5)
            group_frame.grid(row=i, column=0, columnspan=4, sticky="ew", pady=5, padx=5)

            tk.Label(group_frame, text="Max Level:").grid(row=0, column=0, sticky="w", padx=2, pady=2)
            tk.Entry(group_frame, textvariable=self.groupcaps_vars[group]["maxlevel"]).grid(row=0, column=1, sticky="ew", padx=2, pady=2)

            tk.Label(group_frame, text="Temps (t1, t2, t3):").grid(row=1, column=0, sticky="w", padx=2, pady=2)
            tk.Entry(group_frame, textvariable=self.groupcaps_vars[group]["times"][1], width=8).grid(row=1, column=1, sticky="ew", padx=2, pady=2)
            tk.Entry(group_frame, textvariable=self.groupcaps_vars[group]["times"][2], width=8).grid(row=1, column=2, sticky="ew", padx=2, pady=2)
            tk.Entry(group_frame, textvariable=self.groupcaps_vars[group]["times"][3], width=8).grid(row=1, column=3, sticky="ew", padx=2, pady=2)

            tk.Label(group_frame, text="Uses:").grid(row=2, column=0, sticky="w", padx=2, pady=2)
            tk.Entry(group_frame, textvariable=self.groupcaps_vars[group]["uses"]).grid(row=2, column=1, sticky="ew", padx=2, pady=2)
        
        # max_drop_level (displayed but not editable, as per previous instruction)
        tk.Label(tool_frame, text="Max Drop Level:").grid(row=len(["cracky", "choppy", "crumbly", "snappy"]), column=0, sticky="w", padx=5, pady=2)
        tk.Label(tool_frame, textvariable=self.max_drop_level_var).grid(row=len(["cracky", "choppy", "crumbly", "snappy"]), column=1, sticky="w", padx=5, pady=2)


        # --- Boutons de contrôle ---
        button_frame = tk.Frame(editor_window, padx=10, pady=10)
        button_frame.pack(fill="x", side="bottom")

        def save_tool_capabilities():
            try:
                # Construire le dictionnaire des capacités de l'outil à partir des variables Tkinter
                tool_caps = {
                    "damage_groups": {
                        "fleshy": self.fleshy_damage_var.get()
                    },
                    "full_punch_interval": self.full_punch_interval_var.get(),
                    "groupcaps": {},
                    "max_drop_level": self.max_drop_level_var.get() # Inclure la valeur fixe
                }
                for group in ["cracky", "choppy", "crumbly", "snappy"]:
                    times_list = [None] # Le premier élément est toujours null
                    for i in range(1, 4):
                        try:
                            times_list.append(self.groupcaps_vars[group]["times"][i].get())
                        except ValueError:
                            messagebox.showerror("Erreur de saisie", f"Veuillez entrer un nombre valide pour 'Temps' dans {group}.")
                            return
                    
                    tool_caps["groupcaps"][group] = {
                        "maxlevel": self.groupcaps_vars[group]["maxlevel"].get(),
                        "times": times_list,
                        "uses": self.groupcaps_vars[group]["uses"].get()
                    }
                
                self.tool_capabilities_data = tool_caps # Met à jour les données internes
                editor_window.destroy()
                editor_window.grab_release()
                self._update_command_display()

            except ValueError as e:
                messagebox.showerror("Erreur de saisie", f"Veuillez vérifier vos entrées numériques: {e}")

        def reset_to_defaults():
            # Réinitialiser les variables Tkinter aux valeurs par défaut
            self.fleshy_damage_var.set(DEFAULT_TOOL_CAPS_DICT["damage_groups"]["fleshy"])
            self.full_punch_interval_var.set(DEFAULT_TOOL_CAPS_DICT["full_punch_interval"])
            self.max_drop_level_var.set(DEFAULT_TOOL_CAPS_DICT["max_drop_level"])

            for group in ["cracky", "choppy", "crumbly", "snappy"]:
                self.groupcaps_vars[group]["maxlevel"].set(DEFAULT_TOOL_CAPS_DICT["groupcaps"][group]["maxlevel"])
                for i in range(1, 4):
                    self.groupcaps_vars[group]["times"][i].set(DEFAULT_TOOL_CAPS_DICT["groupcaps"][group]["times"][i])
                self.groupcaps_vars[group]["uses"].set(DEFAULT_TOOL_CAPS_DICT["groupcaps"][group]["uses"])
            
            messagebox.showinfo("Réinitialisé", "Les valeurs par défaut ont été rechargées dans l'éditeur. Cliquez sur 'Confirmer' pour les appliquer.")

        def cancel_editor():
            # Quand on annule, on veut que la métadonnée disparaisse de la commande finale
            self.tool_capabilities_data = None
            editor_window.destroy()
            editor_window.grab_release()
            self._update_command_display() # Met à jour la commande finale

        btn_confirm = tk.Button(button_frame, text="Confirmer", command=save_tool_capabilities)
        btn_confirm.pack(side="right", padx=5)

        btn_reset = tk.Button(button_frame, text="Réinitialiser aux valeurs par défaut", command=reset_to_defaults)
        btn_reset.pack(side="left", padx=5)

        btn_cancel = tk.Button(button_frame, text="Annuler", command=cancel_editor)
        btn_cancel.pack(side="right", padx=5) # Placé à droite pour être près de Confirmer

        editor_window.protocol("WM_DELETE_WINDOW", lambda: (editor_window.destroy(), editor_window.grab_release()))


    def _copy_command(self):
        command_text = self.command_display.get(1.0, END).strip()
        if self.root.clipboard_clear:
            self.root.clipboard_clear()
        self.root.clipboard_append(command_text)
        messagebox.showinfo("Copié !", "La commande a été copiée dans le presse-papiers.")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
