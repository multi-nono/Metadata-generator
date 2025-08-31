import tkinter as tk
from tkinter import colorchooser, messagebox, Toplevel, Text, Scrollbar, END, INSERT
import re
import json
DEFAULT_TOOL_CAPS_DICT = {
    "damage_groups": {"fleshy": 1.0},
    "full_punch_interval": 0.5,
    "groupcaps": {
        "cracky": {"maxlevel": 3, "times": [None, 1.0, 1.0, 1.0], "uses": 100},
        "choppy": {"maxlevel": 3, "times": [None, 1.0, 1.0, 1.0], "uses": 100},
        "crumbly": {"maxlevel": 3, "times": [None, 1.0, 1.0, 1.0], "uses": 100},
        "snappy": {"maxlevel": 3, "times": [None, 1.0, 1.0, 1.0], "uses": 100}
    },
    "max_drop_level": 1
}

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Generator of metadata 7 Beta (by multi_nono / nono)")
        self.root.geometry("800x450")
        self.root.resizable(False, False)
        self.item_name = tk.StringVar(value="default:stone")
        self.amount = tk.IntVar(value=1)
        self.description_content = ""
        self.short_description_content = ""
        self.item_color_hex = ""
        self.tool_capabilities_data = None 

        self._create_widgets()
        self._update_command_display()

    def _create_widgets(self):
        item_frame = tk.LabelFrame(self.root, text="informations of the object", padx=10, pady=10)
        item_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(item_frame, text="item's string (ex: default:stone):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        item_entry = tk.Entry(item_frame, textvariable=self.item_name, width=40)
        item_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        item_entry.bind("<KeyRelease>", self._on_input_change)

        tk.Label(item_frame, text="Amount:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        amount_entry = tk.Entry(item_frame, textvariable=self.amount, width=10)
        amount_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        amount_entry.bind("<KeyRelease>", self._on_input_change)

        metadata_buttons_frame = tk.LabelFrame(self.root, text="modify metadata", padx=10, pady=10)
        metadata_buttons_frame.pack(pady=10, padx=10, fill="x")

        btn_tool_caps = tk.Button(metadata_buttons_frame, text="tool capabilities", command=self._open_tool_capabilities_editor)
        btn_tool_caps.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        btn_desc = tk.Button(metadata_buttons_frame, text="description", command=self._open_description_editor)
        btn_desc.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        btn_short_desc = tk.Button(metadata_buttons_frame, text="short description", command=self._open_short_description_editor)
        btn_short_desc.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        btn_item_color = tk.Button(metadata_buttons_frame, text="item's color", command=self._open_item_color_picker)
        btn_item_color.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        command_frame = tk.LabelFrame(self.root, text="command generated :", padx=10, pady=10)
        command_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.command_display = Text(command_frame, wrap="word", height=5, state="disabled", bg="lightgray", font=("Courier", 10))
        self.command_display.pack(fill="both", expand=True, padx=5, pady=5)

        command_control_frame = tk.Frame(self.root)
        command_control_frame.pack(pady=5)

        copy_button = tk.Button(command_control_frame, text="copy the command", command=self._copy_command)
        copy_button.pack(side="left", padx=5)

        

    def _on_input_change(self, event=None):
        self._update_command_display()

    def _update_command_display(self):
        item_name = self.item_name.get()
        amount = self.amount.get()

        all_metadata_blocks = []


        if self.tool_capabilities_data is not None:
            tool_caps_json_raw = json.dumps(self.tool_capabilities_data, separators=(',', ':'))
            tool_caps_json_escaped = tool_caps_json_raw.replace('"', '\\"')
            all_metadata_blocks.append(f"\\u0001x_enchanting\\u0002\\u0003tool_capabilities\\u0002{tool_caps_json_escaped}")

        if self.description_content:
            all_metadata_blocks.append(f"\\u0003description\\u0002{self.description_content}")

        if self.short_description_content:
            all_metadata_blocks.append(f"\\u0003short_description\\u0002{self.short_description_content}")

        final_metadata_string_core = "".join(all_metadata_blocks)

        item_color_block = ""
        if self.item_color_hex:
            item_color_block = f"\\u001bE\\u0003color\\u0002{self.item_color_hex}\\u0003"
        
        final_terminator_u0003 = ""
        if final_metadata_string_core and not item_color_block:
            final_terminator_u0003 = "\\u0003"

        final_metadata_string = final_metadata_string_core + final_terminator_u0003 + item_color_block

        command = f"/giveme {item_name} {amount} 0 \"{final_metadata_string}\""

        self.command_display.config(state="normal")
        self.command_display.delete(1.0, END)
        self.command_display.insert(END, command)
        self.command_display.config(state="disabled")

    def _open_description_editor(self):
        self._open_text_editor("description (in the inventory)", self.description_content, self._set_description_content)

    def _open_short_description_editor(self):
        self._open_text_editor("short description (when you take it in hand)", self.short_description_content, self._set_short_description_content)

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
                toggle_button.config(text="hide color's code")
            else:
                toggle_button.config(text="show color's code")
            _apply_formatting()

        btn_insert_color = tk.Button(button_frame, text="pick a color", command=insert_color_code)
        btn_insert_color.pack(side="left", padx=5)
        
        toggle_button = tk.Button(button_frame, text="hide color's code" if editor_window.show_codes else "show color's code", command=toggle_code_visibility)
        toggle_button.pack(side="left", padx=5)

        btn_confirm = tk.Button(button_frame, text="submit", command=confirm_text)
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
        self._update_command_display()

    def _set_short_description_content(self, content):
        self.short_description_content = content
        self._update_command_display()

    def _open_item_color_picker(self):
        color_window = Toplevel(self.root)
        color_window.title("Item's color")
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

        tk.Label(color_window, text="selected color :").pack(pady=5)
        color_display_label = tk.Label(color_window, bg=chosen_color.get(), width=10, height=2, relief="sunken")
        color_display_label.pack(pady=5)

        btn_pick = tk.Button(color_window, text="pick a color", command=pick_color)
        btn_pick.pack(pady=5)

        btn_confirm = tk.Button(color_window, text="submit", command=confirm_color)
        btn_confirm.pack(pady=5)
        
        btn_cancel = tk.Button(color_window, text="remove the color", command=cancel_color)
        btn_cancel.pack(pady=5)
        
        color_window.protocol("WM_DELETE_WINDOW", lambda: (color_window.destroy(), color_window.grab_release()))


    def _copy_command(self):
        command_text = self.command_display.get(1.0, END).strip()
        if self.root.clipboard_clear:
            self.root.clipboard_clear()
        self.root.clipboard_append(command_text)
        messagebox.showinfo("Copied !", "the command has been copied")

    def _open_tool_capabilities_editor(self):
        editor_window = Toplevel(self.root)
        editor_window.title("modify tool capabilities")
        editor_window.geometry("600x700")
        editor_window.transient(self.root)
        editor_window.grab_set()

        current_data_for_editor = self.tool_capabilities_data if self.tool_capabilities_data is not None else DEFAULT_TOOL_CAPS_DICT.copy()

        self.fleshy_damage_var = tk.DoubleVar(value=current_data_for_editor["damage_groups"].get("fleshy", 1.0))
        self.full_punch_interval_var = tk.DoubleVar(value=current_data_for_editor.get("full_punch_interval", 0.5))

        self.groupcaps_vars = {}
        for group in ["cracky", "choppy", "crumbly", "snappy"]:
            self.groupcaps_vars[group] = {
                "maxlevel": tk.IntVar(value=current_data_for_editor["groupcaps"].get(group, {}).get("maxlevel", 3)),
                "times": [
                    tk.StringVar(value="null"),
                    tk.DoubleVar(value=current_data_for_editor["groupcaps"].get(group, {}).get("times", [None, 1.0, 1.0, 1.0])[1]),
                    tk.DoubleVar(value=current_data_for_editor["groupcaps"].get(group, {}).get("times", [None, 1.0, 1.0, 1.0])[2]),
                    tk.DoubleVar(value=current_data_for_editor["groupcaps"].get(group, {}).get("times", [None, 1.0, 1.0, 1.0])[3])
                ],
                "uses": tk.IntVar(value=current_data_for_editor["groupcaps"].get(group, {}).get("uses", 100))
            }
        

        self.max_drop_level_var = tk.IntVar(value=current_data_for_editor.get("max_drop_level", 1))

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


        weapon_frame = tk.LabelFrame(scrollable_frame, text="Weapon", padx=10, pady=10)
        weapon_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(weapon_frame, text="damages (fleshy):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        tk.Entry(weapon_frame, textvariable=self.fleshy_damage_var).grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        tk.Label(weapon_frame, text="typing speed (full_punch_interval):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        tk.Entry(weapon_frame, textvariable=self.full_punch_interval_var).grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        tool_frame = tk.LabelFrame(scrollable_frame, text="tool", padx=10, pady=10)
        tool_frame.pack(pady=10, padx=10, fill="x")

        for i, group in enumerate(["cracky", "choppy", "crumbly", "snappy"]):
            group_frame = tk.LabelFrame(tool_frame, text=f"{group.capitalize()}", padx=5, pady=5)
            group_frame.grid(row=i, column=0, columnspan=4, sticky="ew", pady=5, padx=5)

            tk.Label(group_frame, text="Max Level:").grid(row=0, column=0, sticky="w", padx=2, pady=2)
            tk.Entry(group_frame, textvariable=self.groupcaps_vars[group]["maxlevel"]).grid(row=0, column=1, sticky="ew", padx=2, pady=2)

            tk.Label(group_frame, text="Times (lv1, lv2, lv3):").grid(row=1, column=0, sticky="w", padx=2, pady=2)
            tk.Entry(group_frame, textvariable=self.groupcaps_vars[group]["times"][1], width=8).grid(row=1, column=1, sticky="ew", padx=2, pady=2)
            tk.Entry(group_frame, textvariable=self.groupcaps_vars[group]["times"][2], width=8).grid(row=1, column=2, sticky="ew", padx=2, pady=2)
            tk.Entry(group_frame, textvariable=self.groupcaps_vars[group]["times"][3], width=8).grid(row=1, column=3, sticky="ew", padx=2, pady=2)

            tk.Label(group_frame, text="Uses:").grid(row=2, column=0, sticky="w", padx=2, pady=2)
            tk.Entry(group_frame, textvariable=self.groupcaps_vars[group]["uses"]).grid(row=2, column=1, sticky="ew", padx=2, pady=2)
        
        tk.Label(tool_frame, text="Max Drop Level:").grid(row=len(["cracky", "choppy", "crumbly", "snappy"]), column=0, sticky="w", padx=5, pady=2)
        tk.Label(tool_frame, textvariable=self.max_drop_level_var).grid(row=len(["cracky", "choppy", "crumbly", "snappy"]), column=1, sticky="w", padx=5, pady=2)


        button_frame = tk.Frame(editor_window, padx=10, pady=10)
        button_frame.pack(fill="x", side="bottom")

        def save_tool_capabilities():
            try:
                tool_caps = {
                    "damage_groups": {
                        "fleshy": self.fleshy_damage_var.get()
                    },
                    "full_punch_interval": self.full_punch_interval_var.get(),
                    "groupcaps": {},
                    "max_drop_level": self.max_drop_level_var.get()
                }
                for group in ["cracky", "choppy", "crumbly", "snappy"]:
                    times_list = [None]
                    for i in range(1, 4):
                        try:
                            times_list.append(self.groupcaps_vars[group]["times"][i].get())
                        except ValueError:
                            messagebox.showerror("eror 401", f"enter a valid number in 'Temps' in {group}.")
                            return
                    
                    tool_caps["groupcaps"][group] = {
                        "maxlevel": self.groupcaps_vars[group]["maxlevel"].get(),
                        "times": times_list,
                        "uses": self.groupcaps_vars[group]["uses"].get()
                    }
                
                self.tool_capabilities_data = tool_caps
                editor_window.destroy()
                editor_window.grab_release()
                self._update_command_display()

            except ValueError as e:
                messagebox.showerror("Eror", f"verify numeric value: {e}")

        def reset_to_defaults():
            self.fleshy_damage_var.set(DEFAULT_TOOL_CAPS_DICT["damage_groups"]["fleshy"])
            self.full_punch_interval_var.set(DEFAULT_TOOL_CAPS_DICT["full_punch_interval"])
            self.max_drop_level_var.set(DEFAULT_TOOL_CAPS_DICT["max_drop_level"])

            for group in ["cracky", "choppy", "crumbly", "snappy"]:
                self.groupcaps_vars[group]["maxlevel"].set(DEFAULT_TOOL_CAPS_DICT["groupcaps"][group]["maxlevel"])
                for i in range(1, 4):
                    self.groupcaps_vars[group]["times"][i].set(DEFAULT_TOOL_CAPS_DICT["groupcaps"][group]["times"][i])
                self.groupcaps_vars[group]["uses"].set(DEFAULT_TOOL_CAPS_DICT["groupcaps"][group]["uses"])
            
            messagebox.showinfo("Reset", "the defaults value as been set in the editor, click 'submit' to aply")

        def cancel_editor():
            self.tool_capabilities_data = None
            editor_window.destroy()
            editor_window.grab_release()
            self._update_command_display()

        btn_confirm = tk.Button(button_frame, text="submit", command=save_tool_capabilities)
        btn_confirm.pack(side="right", padx=5)

        btn_reset = tk.Button(button_frame, text="reset", command=reset_to_defaults)
        btn_reset.pack(side="left", padx=5)

        btn_cancel = tk.Button(button_frame, text="remove tool capability", command=cancel_editor)
        btn_cancel.pack(side="right", padx=5)

        editor_window.protocol("WM_DELETE_WINDOW", lambda: (editor_window.destroy(), editor_window.grab_release()))


    def _copy_command(self):
        command_text = self.command_display.get(1.0, END).strip()
        if self.root.clipboard_clear:
            self.root.clipboard_clear()
        self.root.clipboard_append(command_text)
        messagebox.showinfo("Copied !", "the command has been copied")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
