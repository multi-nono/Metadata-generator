import tkinter as tk
from tkinter import colorchooser, messagebox, Toplevel, Text, Scrollbar, END, INSERT
import re
import json # Pour gérer les données JSON des capacités de l'outil

# Define the default tool capabilities string exactly as provided by the user
# This string is now only used as a reference for the default JSON data.
DEFAULT_TOOL_CAPS_STRING = "\\u0003tool_capabilities\\u0002{\"damage_groups\": {\"fleshy\": 1},\"full_punch_interval\": 0.5,\"groupcaps\": {\"cracky\": {\"maxlevel\": 3, \"times\": [null, 1, 1, 1], \"uses\": 100},\"choppy\": {\"maxlevel\": 1, \"times\": [null, 1, 1, 1], \"uses\": 100},\"crumbly\": {\"maxlevel\": 3, \"times\": [null, 1, 1, 1], \"uses\": 100},\"snappy\": {\"maxlevel\": 3, \"times\": [null, 1, 1, 1], \"uses\": 100}},\"max_drop_level\": 1}\\u0003"

# Extract the JSON part from DEFAULT_TOOL_CAPS_STRING for initial data loading
# This regex matches the part between \u0002 and the final \u0003
DEFAULT_TOOL_CAPS_JSON_PART_MATCH = re.search(r'\\u0002({.*?})\\u0003$', DEFAULT_TOOL_CAPS_STRING)
if DEFAULT_TOOL_CAPS_JSON_PART_MATCH:
    DEFAULT_TOOL_CAPS_DICT = json.loads(DEFAULT_TOOL_CAPS_JSON_PART_MATCH.group(1))
else:
    DEFAULT_TOOL_CAPS_DICT = {} # Fallback if regex fails

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
        # Données pour les capacités de l'outil, initialisées à None (pas de capacités par défaut dans la commande)
        self.tool_capabilities_data = None 

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

        # Nouveau bouton pour les capacités de l'outil
        btn_tool_caps = tk.Button(metadata_buttons_frame, text="Capacités de l'outil", command=self._open_tool_capabilities_editor)
        btn_tool_caps.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        btn_desc = tk.Button(metadata_buttons_frame, text="Modifier Description", command=self._open_description_editor)
        btn_desc.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        btn_short_desc = tk.Button(metadata_buttons_frame, text="Modifier Description Courte", command=self._open_short_description_editor)
        btn_short_desc.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        btn_item_color = tk.Button(metadata_buttons_frame, text="Modifier Couleur de l'Item", command=self._open_item_color_picker)
        btn_item_color.grid(row=0, column=3, padx=5, pady=5, sticky="ew") # Nouvelle colonne pour ce bouton

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

        metadata_parts_list = []
        item_color_part = ""

        # 1. Capacités de l'outil (première priorité)
        if self.tool_capabilities_data is not None: # Seulement si des données ont été définies/modifiées
            tool_caps_json_raw = json.dumps(self.tool_capabilities_data) # Génère JSON avec espaces
            # Échapper les guillemets internes pour Luanti
            tool_caps_json_escaped = tool_caps_json_raw.replace('"', '\\"')
            metadata_parts_list.append(f"\\u0003tool_capabilities\\u0002{tool_caps_json_escaped}\\u0003")


        # 2. Description
        if self.description_content:
            metadata_parts_list.append(f"\\u0003description\\u0002{self.description_content}\\u0003")

        # 3. Description Courte
        if self.short_description_content:
            metadata_parts_list.append(f"\\u0003short_description\\u0002{self.short_description_content}\\u0003")

        # 4. Couleur de l'item (traitement spécial car elle inclut son propre \u0003 final et \u001bE)
        if self.item_color_hex:
            item_color_part = f"\\u001bE\\u0003color\\u0002{self.item_color_hex}\\u0003"

        # Construire la chaîne finale des métadonnées
        final_metadata_string = "".join(metadata_parts_list)
        
        # Add item_color_part at the very end (it contains its own \u0003)
        final_metadata_string += item_color_part

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
        color_window.geometry("300x180")
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

    # --- Nouvelle fonction pour l'éditeur de capacités de l'outil ---
    def _open_tool_capabilities_editor(self):
        editor_window = Toplevel(self.root)
        editor_window.title("Modifier Capacités de l'Outil")
        editor_window.geometry("600x700") # Taille ajustée pour plus de champs
        editor_window.transient(self.root)
        editor_window.grab_set()

        # Valeurs par défaut pour les capacités de l'outil
        default_tool_caps_data = {
            "damage_groups": {"fleshy": 1},
            "full_punch_interval": 0.5,
            "groupcaps": {
                "cracky": {"maxlevel": 3, "times": [None, 1, 1, 1], "uses": 100},
                "choppy": {"maxlevel": 1, "times": [None, 1, 1, 1], "uses": 100},
                "crumbly": {"maxlevel": 3, "times": [None, 1, 1, 1], "uses": 100},
                "snappy": {"maxlevel": 3, "times": [None, 1, 1, 1], "uses": 100}
            },
            "max_drop_level": 1
        }

        # Initialiser les variables Tkinter avec les données actuelles (si elles existent) ou les valeurs par default
        # Si tool_capabilities_data est None, on utilise les valeurs par défaut pour l'affichage dans l'éditeur.
        # Si tool_capabilities_data n'est pas None, on utilise ses valeurs.
        current_data_for_editor = self.tool_capabilities_data if self.tool_capabilities_data is not None else default_tool_caps_data

        # Variables pour les dégâts aux entités
        self.fleshy_damage = tk.DoubleVar(value=current_data_for_editor["damage_groups"].get("fleshy", 1))
        self.full_punch_interval = tk.DoubleVar(value=current_data_for_editor.get("full_punch_interval", 0.5))

        # Variables pour le cassage des blocs
        self.groupcaps_vars = {}
        for group in ["cracky", "choppy", "crumbly", "snappy"]:
            self.groupcaps_vars[group] = {
                "maxlevel": tk.IntVar(value=current_data_for_editor["groupcaps"].get(group, {}).get("maxlevel", 3)),
                "times": [
                    tk.StringVar(value="null"), # Le premier est toujours null
                    tk.DoubleVar(value=current_data_for_editor["groupcaps"].get(group, {}).get("times", [None, 1, 1, 1])[1]),
                    tk.DoubleVar(value=current_data_for_editor["groupcaps"].get(group, {}).get("times", [None, 1, 1, 1])[2]),
                    tk.DoubleVar(value=current_data_for_editor["groupcaps"].get(group, {}).get("times", [None, 1, 1, 1])[3])
                ],
                "uses": tk.IntVar(value=current_data_for_editor["groupcaps"].get(group, {}).get("uses", 100))
            }
        
        # max_drop_level (read-only for now, as not explicitly requested to be editable)
        self.max_drop_level = tk.IntVar(value=current_data_for_editor.get("max_drop_level", 1))

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


        # --- Dégâts aux entités ---
        damage_frame = tk.LabelFrame(scrollable_frame, text="Dégâts aux entités", padx=10, pady=10)
        damage_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(damage_frame, text="Dégâts (fleshy):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        tk.Entry(damage_frame, textvariable=self.fleshy_damage).grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        tk.Label(damage_frame, text="Intervalle de frappe (full_punch_interval):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        tk.Entry(damage_frame, textvariable=self.full_punch_interval).grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        # --- Cassage des blocs ---
        block_breaking_frame = tk.LabelFrame(scrollable_frame, text="Cassage des blocs", padx=10, pady=10)
        block_breaking_frame.pack(pady=10, padx=10, fill="x")

        for i, group in enumerate(["cracky", "crumbly", "choppy", "snappy"]):
            group_frame = tk.LabelFrame(block_breaking_frame, text=f"{group.capitalize()} (groupcaps)", padx=5, pady=5)
            group_frame.grid(row=i, column=0, columnspan=2, sticky="ew", pady=5, padx=5)

            tk.Label(group_frame, text="Max Level:").grid(row=0, column=0, sticky="w", padx=2, pady=2)
            tk.Entry(group_frame, textvariable=self.groupcaps_vars[group]["maxlevel"]).grid(row=0, column=1, sticky="ew", padx=2, pady=2)

            tk.Label(group_frame, text="Times (t1, t2, t3):").grid(row=1, column=0, sticky="w", padx=2, pady=2)
            tk.Entry(group_frame, textvariable=self.groupcaps_vars[group]["times"][1], width=8).grid(row=1, column=1, sticky="ew", padx=2, pady=2)
            tk.Entry(group_frame, textvariable=self.groupcaps_vars[group]["times"][2], width=8).grid(row=1, column=2, sticky="ew", padx=2, pady=2)
            tk.Entry(group_frame, textvariable=self.groupcaps_vars[group]["times"][3], width=8).grid(row=1, column=3, sticky="ew", padx=2, pady=2)

            tk.Label(group_frame, text="Uses:").grid(row=2, column=0, sticky="w", padx=2, pady=2)
            tk.Entry(group_frame, textvariable=self.groupcaps_vars[group]["uses"]).grid(row=2, column=1, sticky="ew", padx=2, pady=2)
        
        # max_drop_level (read-only for now, as not explicitly requested to be editable)
        tk.Label(block_breaking_frame, text="Max Drop Level:").grid(row=len(["cracky", "crumbly", "choppy", "snappy"]), column=0, sticky="w", padx=5, pady=2)
        tk.Label(block_breaking_frame, textvariable=self.max_drop_level).grid(row=len(["cracky", "crumbly", "choppy", "snappy"]), column=1, sticky="w", padx=5, pady=2)


        # --- Boutons de contrôle ---
        button_frame = tk.Frame(editor_window, padx=10, pady=10)
        button_frame.pack(fill="x", side="bottom")

        def save_tool_capabilities():
            try:
                # Construire le dictionnaire des capacités de l'outil à partir des variables Tkinter
                tool_caps = {
                    "damage_groups": {
                        "fleshy": self.fleshy_damage.get()
                    },
                    "full_punch_interval": self.full_punch_interval.get(),
                    "groupcaps": {},
                    "max_drop_level": self.max_drop_level.get() # Inclure la valeur fixe
                }
                for group in ["cracky", "choppy", "crumbly", "snappy"]:
                    times_list = [None] # Le premier élément est toujours null
                    for i in range(1, 4):
                        try:
                            times_list.append(self.groupcaps_vars[group]["times"][i].get())
                        except ValueError:
                            messagebox.showerror("Erreur de saisie", f"Veuillez entrer un nombre valide pour 'Times' dans {group}.")
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
            self.fleshy_damage.set(default_tool_caps_data["damage_groups"]["fleshy"])
            self.full_punch_interval.set(default_tool_caps_data["full_punch_interval"])
            self.max_drop_level.set(default_tool_caps_data["max_drop_level"])

            for group in ["cracky", "choppy", "crumbly", "snappy"]:
                self.groupcaps_vars[group]["maxlevel"].set(default_tool_caps_data["groupcaps"][group]["maxlevel"])
                for i in range(1, 4):
                    self.groupcaps_vars[group]["times"][i].set(default_tool_caps_data["groupcaps"][group]["times"][i])
                self.groupcaps_vars[group]["uses"].set(default_tool_caps_data["groupcaps"][group]["uses"])
            
            # Ne pas modifier self.tool_capabilities_data ici. L'utilisateur doit cliquer "Confirmer" pour sauvegarder.
            messagebox.showinfo("Réinitialisé", "Les valeurs par défaut ont été rechargées dans l'éditeur. Cliquez sur 'Confirmer' pour les appliquer.")
            # Pas besoin de _update_command_display ici, car l'état interne n'a pas changé pour la commande finale.

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
