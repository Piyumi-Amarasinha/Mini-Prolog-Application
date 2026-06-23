import customtkinter as ctk
from tkinter import messagebox, filedialog
from tkinter import X, BOTH, LEFT, RIGHT, TOP
from datetime import datetime
from pyswip import Prolog

# Set the appearance mode and default color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


# Veterinary Triage Expert System (CustomTkinter GUI)


LEVEL_META = {
    'emergency':   {'color': '#E74C3C', 'icon': '\U0001F7E5'},
    'urgent':      {'color': '#E67E22', 'icon': '\U0001F7E7'},
    'non_urgent':  {'color': '#3498DB', 'icon': '\U0001F7E8'},
    'advice':      {'color': '#2ECC71', 'icon': '\U0001F7E6'},
    'observation': {'color': '#95A5A6', 'icon': '❓'},
}

SPECIES_ICONS = {'dog': '\U0001F436', 'cat': '\U0001F431', 'bird': '\U0001F426',
                  'rabbit': '\U0001F430', 'other': '\U0001F43E'}

# (field name, Prolog predicate, question label, choices)
QUESTIONS = [
    ("species", "species", "1. What is the animal species?", ['dog', 'cat', 'bird', 'rabbit', 'other']),
    ("severity", "symptom_severity", "2. What is the overall symptom severity?", ['mild', 'moderate', 'severe']),
    ("alertness", "alertness", "3. What is the animal's alertness level?", ['active', 'lethargic', 'unconscious']),
    ("appetite", "appetite", "4. How is the animal's appetite?", ['normal', 'slightly_reduced', 'refused']),
    ("breathing", "breathing_difficulty", "5. Is there any breathing difficulty?", ['no', 'mild', 'yes']),
    ("temperature", "temperature", "6. Any fever or low body temperature?", ['normal', 'fever', 'low']),
    ("vomiting", "vomiting", "7. Is the animal vomiting?", ['none', 'occasional', 'persistent']),
    ("pain", "pain_level", "8. What is the animal's pain level?", ['none', 'mild', 'severe']),
    ("hydration", "hydration", "9. Any signs of dehydration?", ['normal', 'dehydrated']),
]

WEIGHT_LABELS = [
    ('Ws', 'Severity'), ('Wa', 'Alertness'), ('Wap', 'Appetite'), ('Wb', 'Breathing'),
    ('Wt', 'Temperature'), ('Wv', 'Vomiting'), ('Wpn', 'Pain'), ('Wh', 'Hydration'),
]


def _decode(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except Exception:
            return value.decode(errors='ignore')
    return value


def _to_int(value, default=0):
    value = _decode(value)
    try:
        return int(value)
    except Exception:
        pass
    try:
        return int(float(value))
    except Exception:
        return default


def _to_float(value, default=0.0):
    value = _decode(value)
    try:
        return float(value)
    except Exception:
        return default


class TriageApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Veterinary Triage Assistant")
        self.geometry("820x880")
        self.minsize(760, 600)

        self.last_report = None
        self.engine_ready = True
        self.prolog = None

        self._init_prolog()
        self.create_widgets()

        if not self.engine_ready:
            self.diagnose_button.configure(state="disabled")
            self.status_label.configure(
                text="⚠ Prolog engine unavailable - install SWI-Prolog and check rules.pl, then restart.")

    def _init_prolog(self):
        try:
            self.prolog = Prolog()
        except Exception as e:
            self.engine_ready = False
            messagebox.showerror(
                'Prolog Error',
                f'Could not start the Prolog engine: {e}\nEnsure SWI-Prolog is installed and accessible.')
            return

        try:
            self.prolog.consult('rules.pl')
        except Exception as e:
            self.engine_ready = False
            messagebox.showerror(
                'Prolog Error',
                f'Could not load rules.pl: {e}\nEnsure rules.pl is in the same folder as this script.')

    def create_widgets(self):

        # 1. System Title + theme toggle
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(side=TOP, fill=X, padx=20, pady=(15, 10))

        self.species_icon_label = ctk.CTkLabel(top_frame, text=SPECIES_ICONS['dog'],
                                                font=ctk.CTkFont(size=30), text_color="black")
        self.species_icon_label.pack(side=LEFT, padx=(0, 8))

        title_label = ctk.CTkLabel(top_frame,
                                   text="VETERINARY TRIAGE SYSTEM",
                                   font=ctk.CTkFont(size=20, weight="bold"),
                                   text_color=("#3498db", "#2980b9"))
        title_label.pack(side=LEFT)

        self.theme_switch = ctk.CTkSwitch(top_frame, text="Dark mode",
                                          command=self.toggle_theme, font=ctk.CTkFont(size=12))
        self.theme_switch.pack(side=RIGHT)

        self.status_label = ctk.CTkLabel(self, text="", text_color="#E74C3C",
                                         font=ctk.CTkFont(size=12, weight="bold"))
        self.status_label.pack(side=TOP, pady=(0, 5))

        # Two pages: the Diagnosis tab holds the inputs and a quick result,
        # the Details tab holds the breakdown/explanation/history - kept out
        # of the way until the user actually wants to dig into them.
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))
        self.tabview.add("Diagnosis")
        self.tabview.add("Details")

        diagnosis_scroll = ctk.CTkScrollableFrame(self.tabview.tab("Diagnosis"), fg_color="transparent")
        diagnosis_scroll.pack(fill=BOTH, expand=True)

        details_scroll = ctk.CTkScrollableFrame(self.tabview.tab("Details"), fg_color="transparent")
        details_scroll.pack(fill=BOTH, expand=True)

        # Create a main frame to hold all inputs
        input_frame = ctk.CTkFrame(diagnosis_scroll, corner_radius=10, fg_color="#CBDBF4")
        input_frame.pack(fill=X, pady=10, ipady=10)

        for ci in range(1, 8):
            input_frame.columnconfigure(ci, weight=1)
        input_frame.columnconfigure(0, weight=1)

        # --- Helper function for cleaner code ---
        def create_input_row(parent_frame, row_index, label_text, choices, on_change=None):
            label = ctk.CTkLabel(parent_frame, text=label_text, font=ctk.CTkFont(size=14, weight="bold"))
            label.grid(row=row_index, column=0, sticky="w", padx=20, pady=12)

            var = ctk.StringVar(value=choices[0])

            def handle_change():
                if on_change:
                    on_change(var.get())

            # Place radio buttons horizontally in the input_frame so columns align across rows.
            for ci, choice in enumerate(choices):
                display = choice.replace('_', ' ')
                rb = ctk.CTkRadioButton(parent_frame, text=display, variable=var, value=choice,
                                        font=ctk.CTkFont(size=12), command=handle_change)
                rb.grid(row=row_index, column=1 + ci, padx=8, pady=6, sticky="w")

            return var

        # 2. Input Rows (built generically from QUESTIONS)
        self.vars = {}
        self._var_defaults = []
        for row_index, (name, _predicate, label_text, choices) in enumerate(QUESTIONS):
            on_change = self._update_species_icon if name == "species" else None
            var = create_input_row(input_frame, row_index, label_text, choices, on_change=on_change)
            self.vars[name] = var
            self._var_defaults.append((var, choices[0]))

        # 3. Action buttons
        button_row = ctk.CTkFrame(diagnosis_scroll, fg_color="transparent")
        button_row.pack(pady=(25, 10))

        self.diagnose_button = ctk.CTkButton(button_row, text="Get Triage Recommendation",
                                             command=self.run_diagnosis,
                                             font=ctk.CTkFont(size=16, weight="bold"),
                                             corner_radius=15,
                                             fg_color="#2ECC71",
                                             hover_color="#27AE60")
        self.diagnose_button.pack(side=LEFT, padx=6, ipady=5)

        self.reset_button = ctk.CTkButton(button_row, text="Reset",
                                          command=self.reset_fields,
                                          font=ctk.CTkFont(size=14),
                                          corner_radius=15,
                                          fg_color="#95A5A6",
                                          hover_color="#7F8C8D")
        self.reset_button.pack(side=LEFT, padx=6, ipady=5)

        self.save_button = ctk.CTkButton(button_row, text="Save Report",
                                         command=self.save_report,
                                         font=ctk.CTkFont(size=14),
                                         corner_radius=15,
                                         fg_color="#3498DB",
                                         hover_color="#2E86C1")
        self.save_button.pack(side=LEFT, padx=6, ipady=5)

        # 4. Result Display
        result_frame = ctk.CTkFrame(diagnosis_scroll, fg_color="transparent")
        result_frame.pack(pady=10)

        self.icon_label = ctk.CTkLabel(result_frame, text="", font=ctk.CTkFont(size=30))
        self.icon_label.pack(side=LEFT, padx=(0, 10))

        self.result_label = ctk.CTkLabel(result_frame, text="Click the button to analyze condition.",
                                         font=ctk.CTkFont(size=14, slant="italic"),
                                         wraplength=450, justify=LEFT)
        self.result_label.pack(side=LEFT)

        # Score display (progress bar + label)
        self.score_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        self.score_frame.pack(pady=(5, 0))
        self.score_label = ctk.CTkLabel(self.score_frame, text="Score: -", font=ctk.CTkFont(size=12))
        self.score_label.pack(side=LEFT, padx=(0, 10))
        self.score_bar = ctk.CTkProgressBar(self.score_frame, width=300)
        self.score_bar.set(0.0)
        self.score_bar.pack(side=LEFT)

        # Breakdown + Explanation side-by-side (2 columns)
        cards_row = ctk.CTkFrame(main_scroll, fg_color="transparent")
        cards_row.pack(pady=(8, 0), padx=10, fill=X)
        cards_row.columnconfigure(0, weight=1, uniform="cards")
        cards_row.columnconfigure(1, weight=1, uniform="cards")

        self.breakdown_frame = ctk.CTkFrame(cards_row, corner_radius=8, fg_color="#CBDBF4")
        self.breakdown_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.breakdown_title = ctk.CTkLabel(self.breakdown_frame, text="Severity weight breakdown",
                                            font=ctk.CTkFont(size=12, weight="bold"))
        self.breakdown_title.pack(anchor="w", padx=16, pady=(12, 0))
        self.breakdown_text = ctk.CTkLabel(self.breakdown_frame, text="", font=ctk.CTkFont(size=11),
                                           justify=LEFT, wraplength=320)
        self.breakdown_text.pack(anchor="w", padx=16, pady=(6, 12))

        self.explanation_frame = ctk.CTkFrame(cards_row, corner_radius=8, fg_color="#CBDBF4")
        self.explanation_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.explanation_title = ctk.CTkLabel(self.explanation_frame, text="Why this result?",
                                              font=ctk.CTkFont(size=12, weight="bold"))
        self.explanation_title.pack(anchor="w", padx=16, pady=(12, 0))
        self.explanation_text = ctk.CTkLabel(self.explanation_frame, text="", font=ctk.CTkFont(size=11),
                                             justify=LEFT, wraplength=320)
        self.explanation_text.pack(anchor="w", padx=16, pady=(6, 12))

        # History card
        self.history_frame = ctk.CTkFrame(main_scroll, corner_radius=8, fg_color="#CBDBF4")
        self.history_frame.pack(pady=(8, 16), padx=10, fill=X)
        history_header = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        history_header.pack(fill=X, padx=16, pady=(12, 0))
        ctk.CTkLabel(history_header, text="Diagnosis history",
                    font=ctk.CTkFont(size=12, weight="bold")).pack(side=LEFT)
        ctk.CTkButton(history_header, text="Clear", width=60, command=self.clear_history,
                     font=ctk.CTkFont(size=11)).pack(side=RIGHT)
        self.history_box = ctk.CTkTextbox(self.history_frame, height=120, font=ctk.CTkFont(size=11))
        self.history_box.pack(padx=16, pady=(6, 12), fill=X)
        self.history_box.configure(state="disabled")

    def _update_species_icon(self, species):
        self.species_icon_label.configure(text=SPECIES_ICONS.get(species, SPECIES_ICONS['other']))

    def toggle_theme(self):
        ctk.set_appearance_mode("Dark" if self.theme_switch.get() else "Light")

    def run_diagnosis(self):
        if not self.engine_ready:
            messagebox.showerror('Prolog Error',
                                 'Prolog engine not available. Ensure rules.pl is loaded.')
            return

        values = {name: var.get() for name, var in self.vars.items()}

        try:
            for _name, predicate, _label, _choices in QUESTIONS:
                list(self.prolog.query(f'retractall({predicate}(_))'))
            for name, predicate, _label, _choices in QUESTIONS:
                self.prolog.assertz(f"{predicate}({values[name]})")
        except Exception as e:
            messagebox.showerror('Prolog Error', f'Could not update facts in Prolog: {e}')
            return

        try:
            solutions = list(self.prolog.query(
                'triage_score(Level, Msg, Score, Percent, Ws, Wa, Wap, Wb, Wt, Wv, Wpn, Wh, Mult)'))
        except Exception as e:
            messagebox.showerror('Prolog Error', f'Error querying Prolog: {e}')
            return

        if not solutions:
            messagebox.showwarning('Triage', 'No triage result returned from Prolog.')
            return

        try:
            sol = solutions[0]
            level = _decode(sol.get('Level'))
            message = _decode(sol.get('Msg'))
            score = _to_int(sol.get('Score'))
            percent = _to_int(sol.get('Percent'))
            weights = {label: _to_int(sol.get(key)) for key, label in WEIGHT_LABELS}
            multiplier = _to_float(sol.get('Mult'), 1.0)

            try:
                expl_sols = list(self.prolog.query('explanation(Factors)'))
                factors = [_decode(f) for f in expl_sols[0]['Factors']] if expl_sols else []
            except Exception:
                factors = []

            self._display_result(level, message, score, percent, weights, multiplier, factors, values)
        except Exception as e:
            messagebox.showerror('Unexpected Error', f'Could not display the triage result: {e}')

    def _display_result(self, level, message, score, percent, weights, multiplier, factors, values):
        meta = LEVEL_META.get(level, {'color': '#BDC3C7', 'icon': '\U0001F4A1'})
        color = meta['color']

        self.icon_label.configure(text=meta['icon'], text_color=color)
        self.result_label.configure(text=message, text_color=color, font=ctk.CTkFont(size=16, weight='bold'))

        self.score_label.configure(text=f"Severity score: {percent}% (raw {score})")
        self.score_bar.set(max(0, min(100, percent)) / 100.0)

        breakdown_lines = "\n".join(f"  - {label} weight: {val}" for label, val in weights.items())
        breakdown_lines += f"\n  - Species multiplier: {multiplier}"
        self.breakdown_text.configure(text=breakdown_lines)

        if factors:
            explanation_lines = "\n".join(f"  • {f}" for f in factors)
        else:
            explanation_lines = "  • No significant risk factors identified"
        self.explanation_text.configure(text=explanation_lines)

        timestamp = datetime.now().strftime('%H:%M:%S')
        history_line = f"[{timestamp}] {level.upper()}: {message} (score {percent}%)\n"
        self.history_box.configure(state="normal")
        self.history_box.insert("end", history_line)
        self.history_box.configure(state="disabled")
        self.history_box.see("end")

        self.last_report = self._build_report_text(level, message, score, percent, weights, multiplier,
                                                    factors, values)

        if level == 'emergency':
            messagebox.showerror('Triage Result', message)
        elif level == 'urgent':
            messagebox.showwarning('Triage Result', message)
        else:
            messagebox.showinfo('Triage Result', message)

    def _build_report_text(self, level, message, score, percent, weights, multiplier, factors, values):
        lines = [
            "VETERINARY TRIAGE REPORT",
            "=" * 40,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "Inputs:",
        ]
        for name, _predicate, label, _choices in QUESTIONS:
            lines.append(f"  - {label} {values[name]}")
        lines += [
            "",
            f"Result: {level.upper()}",
            f"Message: {message}",
            f"Severity score: {percent}% (raw {score})",
            "",
            "Weight breakdown:",
        ]
        for label, val in weights.items():
            lines.append(f"  - {label}: {val}")
        lines.append(f"  - Species multiplier: {multiplier}")
        lines += ["", "Contributing factors:"]
        if factors:
            lines += [f"  - {f}" for f in factors]
        else:
            lines.append("  - None identified")
        return "\n".join(lines)

    def reset_fields(self):
        for var, default in self._var_defaults:
            var.set(default)
        self._update_species_icon(self.vars['species'].get())
        self.icon_label.configure(text="")
        self.result_label.configure(text="Click the button to analyze condition.",
                                    text_color=("gray10", "gray90"),
                                    font=ctk.CTkFont(size=14, slant="italic"))
        self.score_label.configure(text="Score: -")
        self.score_bar.set(0.0)
        self.breakdown_text.configure(text="")
        self.explanation_text.configure(text="")
        self.last_report = None

    def clear_history(self):
        self.history_box.configure(state="normal")
        self.history_box.delete("1.0", "end")
        self.history_box.configure(state="disabled")

    def save_report(self):
        if not self.last_report:
            messagebox.showwarning('Save Report', 'Run a diagnosis first before saving a report.')
            return
        path = filedialog.asksaveasfilename(defaultextension='.txt',
                                            filetypes=[('Text files', '*.txt')],
                                            initialfile='triage_report.txt')
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.last_report)
            messagebox.showinfo('Save Report', f'Report saved to {path}')
        except Exception as e:
            messagebox.showerror('Save Report', f'Could not save report: {e}')


# Main loop setup

if __name__ == "__main__":
    app = TriageApp()
    app.mainloop()
