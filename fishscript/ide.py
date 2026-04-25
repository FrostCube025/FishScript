import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from pathlib import Path

from .interpreter import FishScript
from .errors import FishScriptError


KEYWORDS = [
    "AQUARIUM OPENS", "AQUARIUM CLOSES", "HATCH", "AS", "MUTATES INTO",
    "SWALLOWS", "NIBBLES", "SING", "FISH", "FROM VOID", "IF", "OTHERWATER",
    "WHILE", "STILL SWIMMING", "RITUAL", "WITH", "RELEASE", "REEF", "SURFACE",
    "DICEFISH", "LENGTH OF", "CHOOSE FROM", "INDEX", "DROP", "INTO",
    "EAT INDEX", "PANICFISH", "SMELLS LIKE", "SMELLS NOT LIKE",
    "SMELLS LESS THAN", "SMELLS MORE THAN", "EXISTS IN", "BUBBLE",
    "SUM OF", "DIFFERENCE OF", "PRODUCT OF", "QUOTIENT OF", "REMAINDER OF", "AND"
]


DEFAULT_PROGRAM = """AQUARIUM OPENS

BUBBLE Welcome to FishScript

RITUAL DOUBLE WITH fishy
REEF
    fishy SWALLOWS fishy
    RELEASE fishy
SURFACE

HATCH secret AS DICEFISH 1 10
HATCH guess AS 0
HATCH snacks AS ["kelp", "worm", "tiny boot"]

DROP "pizza algae" INTO snacks

SING "Welcome to FishScript."
SING "Random snack:"
SING CHOOSE FROM snacks
SING "Guess the secret fish number."

WHILE secret STILL SWIMMING
REEF
    FISH guess FROM VOID

    IF guess SMELLS LIKE secret
    REEF
        SING "Correct. The fish council respects you."
        secret MUTATES INTO 0
    SURFACE
    OTHERWATER
    REEF
        IF guess SMELLS LESS THAN secret
        REEF
            SING "Too small. Minnow energy."
        SURFACE

        IF guess SMELLS MORE THAN secret
        REEF
            SING "Too big. Whale behavior."
        SURFACE
    SURFACE
SURFACE

SING "Double fish magic:"
SING DOUBLE(5)

PANICFISH

AQUARIUM CLOSES
"""


class FishScriptIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("FishScript IDE")
        self.root.geometry("1100x760")
        self.root.configure(bg="#03111f")
        self.current_file: Path | None = None

        self.bg = "#03111f"
        self.editor_bg = "#0f172a"
        self.output_bg = "#020617"
        self.text = "#e0f2fe"
        self.keyword = "#67e8f9"
        self.string = "#fde68a"
        self.comment = "#94a3b8"
        self.button = "#0891b2"

        self.build_ui()
        self.set_code(DEFAULT_PROGRAM)

    def build_ui(self):
        title = tk.Label(
            self.root,
            text="🐟 FishScript IDE",
            font=("Arial", 24, "bold"),
            bg=self.bg,
            fg=self.keyword,
        )
        title.pack(pady=8)

        toolbar = tk.Frame(self.root, bg=self.bg)
        toolbar.pack(pady=4)

        buttons = [
            ("New", self.new_file),
            ("Open .fish", self.open_file),
            ("Save", self.save_file),
            ("Save As", self.save_as_file),
            ("Run Aquarium", self.run_code),
            ("Clear Output", self.clear_output),
        ]

        for idx, (label, cmd) in enumerate(buttons):
            tk.Button(
                toolbar,
                text=label,
                command=cmd,
                bg=self.button if label == "Run Aquarium" else "#334155",
                fg="white",
                width=14,
            ).grid(row=0, column=idx, padx=4)

        editor_frame = tk.Frame(self.root, bg=self.bg)
        editor_frame.pack(fill="both", expand=True, padx=12, pady=8)

        self.line_numbers = tk.Text(
            editor_frame,
            width=5,
            padx=4,
            takefocus=0,
            border=0,
            bg="#020617",
            fg="#94a3b8",
            state="disabled",
            font=("Consolas", 12),
            wrap="none",
        )
        self.line_numbers.pack(side="left", fill="y")

        self.editor = tk.Text(
            editor_frame,
            font=("Consolas", 12),
            bg=self.editor_bg,
            fg=self.text,
            insertbackground="white",
            undo=True,
            wrap="none",
        )
        self.editor.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(editor_frame, command=self.on_scrollbar)
        scrollbar.pack(side="right", fill="y")

        self.editor.config(yscrollcommand=scrollbar.set)

        self.editor.bind("<KeyRelease>", self.on_change)
        self.editor.bind("<MouseWheel>", self.on_mousewheel)
        self.editor.bind("<ButtonRelease-1>", self.on_change)

        self.editor.tag_configure("keyword", foreground=self.keyword)
        self.editor.tag_configure("string", foreground=self.string)
        self.editor.tag_configure("comment", foreground=self.comment)

        tk.Label(
            self.root,
            text="Output",
            bg=self.bg,
            fg=self.text,
            font=("Arial", 12, "bold"),
        ).pack(anchor="w", padx=12)

        self.output_box = scrolledtext.ScrolledText(
            self.root,
            font=("Consolas", 11),
            bg=self.output_bg,
            fg="#a7f3d0",
            insertbackground="white",
            height=9,
            wrap="word",
        )
        self.output_box.pack(fill="both", padx=12, pady=(0, 12))

    def on_scrollbar(self, *args):
        self.editor.yview(*args)
        self.line_numbers.yview(*args)

    def on_mousewheel(self, event):
        self.root.after(1, self.sync_line_numbers)

    def sync_line_numbers(self):
        self.line_numbers.yview_moveto(self.editor.yview()[0])
        self.update_line_numbers()

    def on_change(self, event=None):
        self.update_line_numbers()
        self.highlight()

    def update_line_numbers(self):
        line_count = int(self.editor.index("end-1c").split(".")[0])
        nums = "\n".join(str(i) for i in range(1, line_count + 1))

        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", nums)
        self.line_numbers.config(state="disabled")

        self.line_numbers.yview_moveto(self.editor.yview()[0])

    def highlight(self):
        for tag in ["keyword", "string", "comment"]:
            self.editor.tag_remove(tag, "1.0", tk.END)

        start = "1.0"
        while True:
            pos = self.editor.search("BUBBLE", start, tk.END)
            if not pos:
                break
            line_end = f"{pos} lineend"
            self.editor.tag_add("comment", pos, line_end)
            start = line_end

        for quote in ['"', "'"]:
            start = "1.0"
            while True:
                pos = self.editor.search(quote, start, tk.END)
                if not pos:
                    break
                end = self.editor.search(quote, f"{pos}+1c", tk.END)
                if not end:
                    break
                self.editor.tag_add("string", pos, f"{end}+1c")
                start = f"{end}+1c"

        for word in sorted(KEYWORDS, key=len, reverse=True):
            start = "1.0"
            while True:
                pos = self.editor.search(word, start, tk.END, nocase=False)
                if not pos:
                    break
                self.editor.tag_add("keyword", pos, f"{pos}+{len(word)}c")
                start = f"{pos}+{len(word)}c"

    def set_code(self, code):
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", code)
        self.on_change()

    def get_code(self):
        return self.editor.get("1.0", "end-1c")

    def new_file(self):
        self.current_file = None
        self.set_code("AQUARIUM OPENS\n\nAQUARIUM CLOSES\n")
        self.root.title("FishScript IDE - Untitled")

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Open FishScript file",
            filetypes=[("FishScript files", "*.fish"), ("All files", "*.*")]
        )

        if not path:
            return

        self.current_file = Path(path)
        self.set_code(self.current_file.read_text(encoding="utf-8"))
        self.root.title(f"FishScript IDE - {self.current_file.name}")

    def save_file(self):
        if self.current_file is None:
            self.save_as_file()
            return

        self.current_file.write_text(self.get_code(), encoding="utf-8")
        self.print_output(f"Saved: {self.current_file}")

    def save_as_file(self):
        path = filedialog.asksaveasfilename(
            title="Save FishScript file",
            defaultextension=".fish",
            filetypes=[("FishScript files", "*.fish"), ("All files", "*.*")]
        )

        if not path:
            return

        self.current_file = Path(path)
        self.save_file()
        self.root.title(f"FishScript IDE - {self.current_file.name}")

    def print_output(self, text):
        self.output_box.insert(tk.END, f"{text}\n")
        self.output_box.see(tk.END)

    def clear_output(self):
        self.output_box.delete("1.0", tk.END)

    def ask_input(self, prompt):
        popup = tk.Toplevel(self.root)
        popup.title("FishScript Void")
        popup.geometry("380x150")
        popup.configure(bg=self.bg)
        popup.grab_set()

        tk.Label(
            popup,
            text=prompt,
            bg=self.bg,
            fg=self.text,
            font=("Arial", 11),
        ).pack(pady=10)

        entry = tk.Entry(
            popup,
            bg=self.editor_bg,
            fg="white",
            insertbackground="white",
            font=("Arial", 12),
        )
        entry.pack(pady=3)
        entry.focus()

        result = {"value": ""}

        def submit():
            result["value"] = entry.get()
            popup.destroy()

        tk.Button(
            popup,
            text="Cast Net",
            command=submit,
            bg=self.button,
            fg="white",
        ).pack(pady=8)

        self.root.wait_window(popup)
        return result["value"]

    def run_code(self):
        self.clear_output()
        self.print_output("🐟 Running FishScript...\n")

        try:
            FishScript(self.print_output, self.ask_input).run(self.get_code())
            self.print_output("\n✅ Aquarium finished.")
        except FishScriptError as error:
            self.print_output(f"\n❌ FishScript Error:\n{error}")
            messagebox.showerror("FishScript Error", str(error))
        except Exception as error:
            self.print_output(f"\n❌ Unexpected Error:\n{error}")
            messagebox.showerror("Unexpected Error", str(error))


def main():
    root = tk.Tk()
    FishScriptIDE(root)
    root.mainloop()


if __name__ == "__main__":
    main()
