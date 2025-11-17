import tkinter as tk
from tkinter import messagebox, ttk
import importlib, os, json, random, re
from io import BytesIO
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import time

# NEW: import the folder-based stats module
from stats_utils import load_progress, save_progress, update_card_result

LEARN_DIR = "learn"

# -------------------------------------------------------
# Helpers
# -------------------------------------------------------

def list_folders():
    return sorted(
        f for f in os.listdir(LEARN_DIR)
        if os.path.isdir(os.path.join(LEARN_DIR, f))
        and not f.startswith("__")
    )

def list_topics(folder):
    folder_path = os.path.join(LEARN_DIR, folder)
    return sorted([
        f[:-3] for f in os.listdir(folder_path)
        if f.endswith(".py")
    ])

def load_cards(full_topic_path):
    mod = importlib.import_module(f"{LEARN_DIR}.{full_topic_path}".replace("/", "."))
    cards = []
    for name in dir(mod):
        func = getattr(mod, name)
        if callable(func) and func.__module__ == mod.__name__:
            try:
                random.seed(time.time_ns() ^ os.getpid())
                data = func()
                if all(k in data for k in ("name", "question", "data_type", "answer", "comparison")):
                    data["topic"] = full_topic_path
                    cards.append(data)
            except Exception as e:
                print("Error in card", name, e)
    return cards

def compare(user, card):
    try:
        if card["data_type"] == "float":
            val = float(user)
            tol = float(card["comparison"].split("=")[1])
            return abs(val - card["answer"]) <= tol
        elif card["data_type"] == "int":
            return int(user) == int(card["answer"])
        else:
            norm = lambda s: re.sub(r"\s+", "", str(s).strip().lower())
            return norm(user) == norm(card["answer"])
    except Exception:
        return False

def render_latex_to_image(latex_str, max_width=500, fontsize=16):
    try:
        latex_str = latex_str.strip("$")
        fig = plt.figure(figsize=(0.01, 0.01))
        fig.patch.set_alpha(0)
        plt.text(0.5, 0.5, f"${latex_str}$", fontsize=fontsize, ha="center", va="center")
        plt.axis("off")
        buf = BytesIO()
        plt.savefig(buf, format="png", dpi=150, bbox_inches="tight", pad_inches=0.1, transparent=True)
        plt.close(fig)
        buf.seek(0)
        img = Image.open(buf).convert("RGBA")
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
        if img.width > max_width:
            scale = max_width / img.width
            img = img.resize((max_width, int(img.height * scale)), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print("Latex render:", e)
        return None

def add_selectable_text(parent, text):
    t = tk.Text(parent, wrap="word", width=80, height=min(20, text.count("\n")+4))
    t.insert("1.0", text)
    t.configure(state="disabled")
    t.pack(pady=8)
    return t

def truncate(s, n=80):
    if not s:
        return ""
    return s if len(s) <= n else s[:n] + " ..."

def show_full_text_popup(parent, title, text):
    top = tk.Toplevel(parent)
    top.title(title)
    txt = tk.Text(top, wrap="word", width=80, height=25)
    txt.insert("1.0", text)
    txt.configure(state="disabled")
    txt.pack(fill="both", expand=True)

def get_accuracy(rec):
    c = rec.get("correct", 0)
    w = rec.get("wrong", 0)
    return c / (c + w) if (c + w) else 0

# -------------------------------------------------------
# GUI
# -------------------------------------------------------

class LearnApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Jürgen ProcKnow - Deep Dive into Knowledge")
        self.geometry("800x600")

        self.current_folder = None
        self.db = {}
        self.all_cards = []
        self.due = []
        self.current = None
        self.peeked = False
        self.repeat_counter = 0
        self.repeat_target = 0

        # ---------------- top bar ----------------
        topbar = tk.Frame(self)
        topbar.pack(fill="x", pady=5)

        # checkbox for weak-only mode
        self.only_weak_var = tk.BooleanVar(value=False)
        self.only_weak_chk = tk.Checkbutton(
            topbar,
            text="Only <75% accuracy",
            variable=self.only_weak_var
        )
        self.only_weak_chk.pack(side="left", padx=10)

        self.folder_var = tk.StringVar()
        self.folder_menu = ttk.Combobox(
            topbar, textvariable=self.folder_var,
            values=list_folders(),
            state="readonly", width=30
        )
        self.folder_menu.pack(side="left", padx=5)
        tk.Button(topbar, text="Load Folder", command=self.load_folder).pack(side="left", padx=5)

        self.topic_var = tk.StringVar()
        self.topic_menu = ttk.Combobox(
            topbar, textvariable=self.topic_var,
            values=["--- load a folder first ---"],
            state="disabled", width=30
        )
        self.topic_var.set("--- load a folder first ---")
        self.topic_menu.pack(side="left", padx=5)

        tk.Button(topbar, text="Load Topic", command=self.load_topic).pack(side="left", padx=5)
        tk.Button(topbar, text="Show Stats", command=self.show_stats).pack(side="left", padx=5)

        # ---------------- scrollable area ----------------
        container = tk.Frame(self, bg="#f8f8f8")
        container.pack(fill="both", expand=True, pady=10)

        canvas = tk.Canvas(container, bg="#f8f8f8", highlightthickness=0)
        vbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        hbar = tk.Scrollbar(container, orient="horizontal", command=canvas.xview)

        scrollable_frame = tk.Frame(canvas, bg="#f8f8f8")
        self.q_frame = scrollable_frame
        self.q_widgets = []

        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(window_id, width=e.width))
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        vbar.pack(side="right", fill="y")
        hbar.pack(side="bottom", fill="x")

        self.q_scroll = canvas

        # footer
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)

        self.ans_entry = tk.Entry(btn_frame, width=40, justify="center")
        self.ans_entry.pack(side="left", padx=5)
        tk.Button(btn_frame, text="Fire!", command=self.submit).pack(side="left", padx=5)

        self.hint_btn = tk.Button(btn_frame, text="Periscope (hint)", command=self.show_hint)
        self.hint_btn.pack(side="left", padx=5)

        self.hint_label = tk.Label(self, text="", font=("Arial", 10, "italic"),
                                   fg="#555", wraplength=700,
                                   justify="center", bg="#f8f8f8")
        self.hint_label.pack(pady=5)

        self.feedback = tk.Label(self, text="", font=("Arial", 11))
        self.feedback.pack(pady=5)

        # verdict action buttons (hidden at first)
        btn_verdict = tk.Frame(self)
        btn_verdict.pack()

        self.accept_btn = tk.Button(btn_verdict, text="Accept verdict", command=self.accept_verdict)
        self.override_btn = tk.Button(btn_verdict, text="Override verdict", command=self.override_verdict)

        self.accept_btn.pack(side="left", padx=5)
        self.override_btn.pack(side="left", padx=5)

        # Start disabled
        self.accept_btn.config(state="disabled")
        self.override_btn.config(state="disabled")

        # cache for user decision
        self.proposed_ok = None
        self.user_answer_cache = None

        self.status = tk.Label(self, text="", anchor="w")
        self.status.pack(fill="x", side="bottom")

    # ---------------------------------------------------
    def load_folder(self):
        folder = self.folder_var.get()
        if not folder:
            messagebox.showinfo("Info", "Select a folder first.")
            return

        self.current_folder = folder
        self.db = load_progress(folder)

        topics = list_topics(folder)
        self.topic_menu.config(values=topics, state="readonly")
        self.topic_var.set("")

    # ---------------------------------------------------
    def load_topic(self):
        if not self.current_folder:
            messagebox.showinfo("Info", "Select and load a folder first.")
            return

        topic = self.topic_var.get()
        if not topic:
            messagebox.showinfo("Info", "Select a topic first.")
            return

        full_topic = f"{self.current_folder}.{topic}"
        self.all_cards = load_cards(full_topic)
        self.due = self.all_cards[:]
        random.shuffle(self.due)

        # filter weak cards if checkbox is active
        if self.only_weak_var.get():
            filtered = []
            prefix = f"{full_topic}."
            for card in self.due:
                key = prefix + card["name"]
                rec = self.db.get(key, {})
                if get_accuracy(rec) < 0.75:
                    filtered.append(card)
            self.due = filtered
            random.shuffle(self.due)

        if not self.due:
            messagebox.showinfo("Info", "No cards in this topic.")
            return

        topic_entries = {
            k: v for k, v in self.db.items()
            if k.startswith(f"{full_topic}.")
        }
        if topic_entries:
            TopicStatsWindow(self, full_topic, topic_entries)

        self.next_card()

    # ---------------------------------------------------
    def next_card(self):
        for w in self.q_widgets:
            w.destroy()
        self.q_widgets.clear()

        self.hint_label.config(text="")
        self.feedback.config(text="")
        self.peeked = False

        # repeat logic
        if (
            self.repeat_target > 0
            and self.repeat_counter < self.repeat_target
            and self.current is not None
        ):
            self.repeat_counter += 1
            func_name = self.current["_func_name"]
            topic = self.current["topic"]
            try:
                mod = importlib.import_module(f"{LEARN_DIR}.{topic}")
                func = getattr(mod, func_name)
                new = func()
                new["topic"] = topic
                new["_func_name"] = func_name
                self.current = new
            except Exception as e:
                print("Repeat error:", e)
        else:
            self.repeat_counter = 0
            self.repeat_target = 0

            if not self.due:
                lbl = tk.Label(self.q_frame, text="All objectives complete. Returning to harbor!",
                               font=("Arial", 13))
                lbl.pack(pady=10)
                self.q_widgets.append(lbl)
                self.current = None
                self.status.config(text="0 cards remaining.")
                self.hint_btn.config(state="disabled")
                return

            self.current = self.due.pop()
            self.repeat_target = self.current.get("repeat", 0)
            self.repeat_counter = 1

            # find the function name
            try:
                topic = self.current["topic"]
                mod = importlib.import_module(f"{LEARN_DIR}.{topic}")
                for name in dir(mod):
                    func = getattr(mod, name)
                    if callable(func) and func.__module__.endswith(topic):
                        try:
                            t = func()
                            if isinstance(t, dict) and t.get("name") == self.current["name"]:
                                self.current["_func_name"] = name
                                break
                        except Exception:
                            continue
            except Exception:
                self.current["_func_name"] = None

        qtext = self.current["question"]
        self.ans_entry.delete(0, tk.END)
        self.status.config(text=f"{len(self.due)} cards remaining")

        if "hint" in self.current:
            self.hint_btn.config(state="normal")
        else:
            self.hint_btn.config(state="disabled")

        parts = re.split(r"(\$.*?\$)", qtext)
        for part in parts:
            if not part:
                continue
            if part.startswith("$") and part.endswith("$"):
                img = render_latex_to_image(part)
                if img:
                    lbl = tk.Label(self.q_frame, image=img, bg="#f8f8f8")
                    lbl.image = img
                    lbl.pack(pady=8)
                    self.q_widgets.append(lbl)
            else:
                widget = add_selectable_text(self.q_frame, part)
                self.q_widgets.append(widget)

    # ---------------------------------------------------
    def render_hint(self, text):
        for w in self.hint_label.winfo_children():
            w.destroy()
        self.hint_label.config(text="")

        parts = re.split(r"(\$.*?\$)", text)
        for part in parts:
            if not part:
                continue
            if part.startswith("$") and part.endswith("$"):
                img = render_latex_to_image(part)
                if img:
                    lbl = tk.Label(self.hint_label, image=img, bg="#f8f8f8")
                    lbl.image = img
                    lbl.pack(side="left", padx=4)
            else:
                lbl = tk.Label(self.hint_label, text=part,
                               font=("Arial", 10, "italic"), fg="#555", bg="#f8f8f8")
                lbl.pack(side="left", padx=4)

    def show_hint(self):
        if self.current and "hint" in self.current:
            self.render_hint(self.current["hint"])
            self.peeked = True
            self.hint_btn.config(state="disabled")

    # ---------------------------------------------------
    def submit(self):
        if not self.current:
            return

        user = self.ans_entry.get()
        ok = compare(user, self.current)

        # cache the proposed verdict
        self.proposed_ok = ok
        self.user_answer_cache = user

        # Display system verdict and correct answer
        verdict_text = "System verdict: CORRECT" if ok else "System verdict: WRONG"
        color = "green" if ok else "red"

        msg = f"{verdict_text}\nYour answer: {user}\nCorrect: {self.current['answer']}"
        self.feedback.config(text=msg, fg=color)

        # Disable hint button
        self.hint_btn.config(state="disabled")

        # Enable accept/override
        self.accept_btn.config(state="normal")
        self.override_btn.config(state="normal")

    def accept_verdict(self):
        """User accepts system's proposed verdict."""
        update_card_result(
            self.current, self.db,
            self.proposed_ok,
            user_answer=self.user_answer_cache
        )
        self.after_user_verdict()


    def override_verdict(self):
        """User flips the verdict."""
        update_card_result(
            self.current, self.db,
            not self.proposed_ok,
            user_answer=self.user_answer_cache
        )
        self.after_user_verdict()


    def after_user_verdict(self):
        """Shared cleanup + show next card."""
        # disable action buttons
        self.accept_btn.config(state="disabled")
        self.override_btn.config(state="disabled")

        # Clean feedback area for next question
        self.feedback.config(text="")

        # next card
        self.next_card()

    # ---------------------------------------------------
    def show_stats(self):
        if not self.current_folder:
            messagebox.showinfo("Info", "Load a folder first.")
            return
        StatsWindow(self, self.db, self.current_folder)


# -------------------------------------------------------
# Stats Window
# -------------------------------------------------------

class StatsWindow(tk.Toplevel):
    def __init__(self, master, db, folder_name):
        super().__init__(master)
        self.title(f"Captain's Log – Folder: {folder_name}")
        self.geometry("700x500")
        self.db = db

        self.sort_key = "accuracy"
        self.sort_reverse = True

        header = tk.Frame(self)
        header.pack(fill="x", pady=5)

        tk.Button(header, text="Sort by Name", command=lambda: self.sort_by("name")).pack(side="left", padx=5)
        tk.Button(header, text="Sort by Correct", command=lambda: self.sort_by("correct")).pack(side="left", padx=5)
        tk.Button(header, text="Sort by Wrong", command=lambda: self.sort_by("wrong")).pack(side="left", padx=5)
        tk.Button(header, text="Sort by Accuracy", command=lambda: self.sort_by("accuracy")).pack(side="left", padx=5)

        total = len(db)
        c = sum(v.get("correct", 0) for v in db.values())
        w = sum(v.get("wrong", 0) for v in db.values())
        acc = (c / (c + w)) * 100 if (c + w) else 0

        tk.Label(self, text=f"Total cards tracked: {total}", font=("Arial", 11)).pack(anchor="w", padx=10)
        tk.Label(self, text=f"Accuracy: {acc:.1f}%", font=("Arial", 11, "bold")).pack(anchor="w", padx=10)

        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, pady=10)

        self.tree = ttk.Treeview(
            frame,
            columns=("name", "correct", "wrong", "accuracy", "wrongs"),
            show="headings"
        )

        for col in ("name", "correct", "wrong", "accuracy", "wrongs"):
            self.tree.heading(col, text=col.capitalize())

        self.tree.column("name", width=220)
        self.tree.column("correct", width=80, anchor="center")
        self.tree.column("wrong", width=80, anchor="center")
        self.tree.column("accuracy", width=100, anchor="center")
        self.tree.column("wrongs", width=200)

        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree.bind("<Double-1>", self.on_double_click)

        self.refresh_table()

        tk.Button(self, text="Close", command=self.destroy).pack(pady=5)

    def sort_by(self, key):
        if self.sort_key == key:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_key = key
            self.sort_reverse = True
        self.refresh_table()

    def refresh_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        rows = []
        for name, rec in self.db.items():
            c = rec.get("correct", 0)
            w = rec.get("wrong", 0)
            acc = (c / (c + w)) * 100 if (c + w) else 0
            full_wrong = ", ".join(rec.get("wrong_log", []))
            rows.append({
                "name": name,
                "correct": c,
                "wrong": w,
                "accuracy": acc,
                "wrongs": truncate(full_wrong)
            })

        rows.sort(key=lambda r: r[self.sort_key], reverse=self.sort_reverse)
        for r in rows:
            self.tree.insert(
                "", "end",
                values=(r["name"], r["correct"], r["wrong"], f"{r['accuracy']:.1f}", r["wrongs"])
            )

    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        values = self.tree.item(item, "values")
        key = values[0]
        rec = self.db.get(key, {})
        full_text = ", ".join(rec.get("wrong_log", [])) or "(none)"
        show_full_text_popup(self, "Full Reflection", full_text)


# -------------------------------------------------------
# Topic Stats Window
# -------------------------------------------------------

class TopicStatsWindow(tk.Toplevel):
    def __init__(self, master, topic, db):
        super().__init__(master)
        self.title(f"Captain's log for '{topic}'")
        self.geometry("600x400")

        tk.Label(self, text=f"Past performance in topic: {topic}",
                 font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=5)

        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, pady=10)

        self.db_local = db

        self.tree = ttk.Treeview(
            frame,
            columns=("name", "correct", "wrong", "accuracy", "wrongs"),
            show="headings"
        )

        for col in ("name", "correct", "wrong", "accuracy", "wrongs"):
            self.tree.heading(col, text=col.capitalize())

        self.tree.column("name", width=220)
        self.tree.column("correct", width=80, anchor="center")
        self.tree.column("wrong", width=80, anchor="center")
        self.tree.column("accuracy", width=100, anchor="center")
        self.tree.column("wrongs", width=200)

        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree.bind("<Double-1>", self.on_double_click)

        for name, rec in sorted(db.items()):
            c = rec.get("correct", 0)
            w = rec.get("wrong", 0)
            acc = (c / (c + w)) * 100 if (c + w) else 0
            full_wrong = ", ".join(rec.get("wrong_log", []))
            self.tree.insert(
                "",
                "end",
                values=(name, c, w, f"{acc:.1f}", truncate(full_wrong))
            )

        tk.Button(self, text="Dive in", command=self.destroy).pack(pady=5)

    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        vals = self.tree.item(item, "values")
        key = vals[0]
        rec = self.db_local.get(key, {})
        full = ", ".join(rec.get("wrong_log", [])) or "(none)"
        show_full_text_popup(self, "Full Reflection", full)


# -------------------------------------------------------
# Main
# -------------------------------------------------------

if __name__ == "__main__":
    print("Jürgen ProcKnow initializing cognitive torpedoes...")
    print("Periscope depth! All minds to learning stations!")
    app = LearnApp()
    app.mainloop()
