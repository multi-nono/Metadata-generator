import tkinter as tk
from tkinter import colorchooser, messagebox, Toplevel, Text, Scrollbar, END, INSERT
import re
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("générateur de Metadata d'item (par Multi_nono / Nono)")
        self.root.geometry("800x450")
        self.root.resizable(False, False)

        self.item_name = tk.StringVar(value="default:stone")
        self.amount = tk.IntVar(value=1)
        self.description_content = ""
        self.short_description_content = ""
        self.item_color_hex = ""

        self._create_widgets()
        self._update_command_display()

    def _create_widgets(self):

        item_frame = tk.LabelFrame(self.root, text="Informations sur l'objet", padx=10, pady=10)
        item_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(item_frame, text="Nom de l'item (ex: default:stone):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        item_entry = tk.Entry(item_frame, textvariable=self.item_name, width=40)
        item_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        item_entry.bind("<KeyRelease>", self._on_input_change)

        tk.Label(item_frame, text="Quantité:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        amount_entry = tk.Entry(item_frame, textvariable=self.amount, width=10)
        amount_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        amount_entry.bind("<KeyRelease>", self._on_input_change)

        metadata_buttons_frame = tk.LabelFrame(self.root, text="Metadata", padx=10, pady=10)
        metadata_buttons_frame.pack(pady=10, padx=10, fill="x")

        btn_desc = tk.Button(metadata_buttons_frame, text="Description", command=self._open_description_editor)
        btn_desc.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        btn_short_desc = tk.Button(metadata_buttons_frame, text="Description Courte", command=self._open_short_description_editor)
        btn_short_desc.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        btn_item_color = tk.Button(metadata_buttons_frame, text="Couleur de l'Item", command=self._open_item_color_picker)
        btn_item_color.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        command_frame = tk.LabelFrame(self.root, text="Commande Générée", padx=10, pady=10)
        command_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.command_display = Text(command_frame, wrap="word", height=5, state="disabled", bg="lightgray", font=("Courier", 10))
        self.command_display.pack(fill="both", expand=True, padx=5, pady=5)

        copy_button = tk.Button(self.root, text="Copier la Commande", command=self._copy_command)
        copy_button.pack(pady=10)

    def _on_input_change(self, event=None):
        self._update_command_display()

    def _update_command_display(self):
        item_name = self.item_name.get()
        amount = self.amount.get()

        metadata_string = ""

        has_standard_metadata_content = False

        if self.description_content:
            metadata_string += f"\\u0003description\\u0002{self.description_content}"
            has_standard_metadata_content = True
        
        if self.short_description_content:
            metadata_string += f"\\u0003short_description\\u0002{self.short_description_content}"
            has_standard_metadata_content = True
        
        if self.item_color_hex:
            metadata_string += f"\\u001bE\\u0003color\\u0002{self.item_color_hex}\\u0003"
        elif has_standard_metadata_content:

            metadata_string += "\\u0003"

        command = f"/giveme {item_name} {amount} 0 \"{metadata_string}\""

        self.command_display.config(state="normal")
        self.command_display.delete(1.0, END)
        self.command_display.insert(END, command)
        self.command_display.config(state="disabled")

    def _open_description_editor(self):
        self._open_text_editor("Description de l'Item (dans l'inventaire)", self.description_content, self._set_description_content)

    def _open_short_description_editor(self):
        self._open_text_editor("Description Courte de l'Item (quand on le prend en main)", self.short_description_content, self._set_short_description_content)

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
            self._update_command_display()

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
        color_window.title("Couleur de l'Item")
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
        
        btn_cancel = tk.Button(color_window, text="enlever la Couleur", command=cancel_color)
        btn_cancel.pack(pady=5)
        
        # Gérer la fermeture de la fenêtre
        color_window.protocol("WM_DELETE_WINDOW", lambda: (color_window.destroy(), color_window.grab_release()))


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
