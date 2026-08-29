import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from rag_engine import RAGEngine

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

BASE = Path(__file__).parent
engine = RAGEngine(BASE)

PURPLE = "#5C2D91"
PURPLE2 = "#7B4BC0"
PURPLE3 = "#EEE7F7"
DARK = "#201A2A"
BG = "#F7F5FA"
CARD = "#FFFFFF"
MUTED = "#746B7D"
ORANGE = "#F59E0B"
GREEN = "#15966A"
BORDER = "#E6DDF0"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WE Intelligent Assistant")
        self.geometry("1380x820")
        self.minsize(1120, 700)
        self.configure(fg_color=BG)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.build_sidebar()
        self.content = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        self.show_home()



    def build_sidebar(self):
        side = ctk.CTkFrame(self, width=255, fg_color=DARK, corner_radius=0)
        side.grid(row=0, column=0, sticky="nsew")
        side.grid_propagate(False)

        logo = ctk.CTkFrame(side, width=64, height=64, fg_color=PURPLE, corner_radius=18)
        logo.pack(anchor="w", padx=28, pady=(32, 12))
        logo.pack_propagate(False)
        ctk.CTkLabel(
            logo, text="WE", text_color="white",
            font=ctk.CTkFont(size=24, weight="bold")
        ).place(relx=.5, rely=.5, anchor="center")

        ctk.CTkLabel(
            side, text="Intelligent\nAssistant",
            text_color="white", justify="left",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(anchor="w", padx=28, pady=(0, 4))

        ctk.CTkLabel(
            side, text="Local RAG • Desktop PoC",
            text_color="#AFA7B8",
            font=ctk.CTkFont(size=11)
        ).pack(anchor="w", padx=28, pady=(0, 28))

        self.nav(side, "⌂   Dashboard", self.show_home)
        self.nav(side, "✦   Smart Assistant", self.show_chat)
        self.nav(side, "▦   Plans Explorer", self.show_plans)
        self.nav(side, "＋   Upload Documents", self.show_upload)
        self.nav(side, "◫   Knowledge Base", self.show_knowledge)
        self.nav(side, "⚙   Architecture", self.show_architecture)

        ctk.CTkLabel(
            side,
            text="Grounded in Telecom Egypt\nknowledge + uploaded documents",
            text_color="#8F8797", justify="left",
            font=ctk.CTkFont(size=10)
        ).pack(side="bottom", anchor="w", padx=28, pady=28)

    def nav(self, parent, text, command):
        b = ctk.CTkButton(
            parent, text=text, command=command,
            height=46, corner_radius=12,
            fg_color="transparent", hover_color=PURPLE,
            text_color="white", anchor="w",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        b.pack(fill="x", padx=18, pady=3)

    def clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    def header(self, title, subtitle):
        top = ctk.CTkFrame(self.content, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=34, pady=(28, 14))
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top, text=title, text_color=DARK,
            font=ctk.CTkFont(size=28, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            top, text=subtitle, text_color=MUTED,
            font=ctk.CTkFont(size=12)
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        chip = ctk.CTkLabel(
            top, text=f"  {engine.chunk_count()} chunks indexed  ",
            fg_color=PURPLE3, text_color=PURPLE, corner_radius=12,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        chip.grid(row=0, column=1, rowspan=2, padx=(15, 0))

    def card(self, parent, **kwargs):
        return ctk.CTkFrame(
            parent, fg_color=CARD, corner_radius=20,
            border_width=1, border_color=BORDER, **kwargs
        )

    def show_home(self):
        self.clear()
        self.header("WE Intelligence Center", "A professional desktop assistant for plans, knowledge retrieval and document querying.")

        body = ctk.CTkFrame(self.content, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=34, pady=(4, 30))
        body.grid_columnconfigure((0,1,2), weight=1)
        body.grid_rowconfigure(2, weight=1)

        hero = ctk.CTkFrame(body, fg_color=PURPLE, corner_radius=24)
        hero.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 18))
        hero.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hero, text="Ask. Retrieve. Answer with evidence.",
            text_color="white",
            font=ctk.CTkFont(size=27, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=30, pady=(26, 5))

        ctk.CTkLabel(
            hero,
            text="Arabic • English • Egyptian dialect • Local documents • Source-aware responses",
            text_color="#E9DCF6",
            font=ctk.CTkFont(size=12)
        ).grid(row=1, column=0, sticky="w", padx=30, pady=(0, 26))

        ctk.CTkButton(
            hero, text="Open Smart Assistant  →",
            command=self.show_chat,
            fg_color=ORANGE, hover_color="#DE8C00",
            text_color=DARK, width=190, height=42,
            corner_radius=14, font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=1, rowspan=2, padx=30)

        stats = [
            ("33", "Plans in catalog", PURPLE),
            (str(engine.chunk_count()), "Knowledge chunks", GREEN),
            ("5+", "Knowledge sources", ORANGE),
        ]
        for i, (value, label, color) in enumerate(stats):
            c = self.card(body)
            c.grid(row=1, column=i, sticky="ew", padx=(0 if i==0 else 8, 0 if i==2 else 8), pady=(0, 18))
            ctk.CTkLabel(c, text=value, text_color=color, font=ctk.CTkFont(size=30, weight="bold")).pack(anchor="w", padx=22, pady=(18, 0))
            ctk.CTkLabel(c, text=label, text_color=MUTED, font=ctk.CTkFont(size=11)).pack(anchor="w", padx=22, pady=(0, 18))

        quick = self.card(body)
        quick.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(quick, text="Quick Actions", text_color=DARK, font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=24, pady=(22, 14))

        actions = [
            ("Find a plan under my budget", self.show_chat),
            ("Browse official plan catalog", self.show_plans),
            ("Add a customer document", self.show_upload),
        ]
        for text, cmd in actions:
            ctk.CTkButton(
                quick, text=text+"   →", command=cmd,
                fg_color="#F6F2FA", hover_color=PURPLE3,
                text_color=PURPLE, anchor="w",
                height=46, corner_radius=12,
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(fill="x", padx=22, pady=6)

        info = self.card(body)
        info.grid(row=2, column=2, sticky="nsew", padx=(8, 0))
        ctk.CTkLabel(info, text="RAG Flow", text_color=DARK, font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=22, pady=(22, 14))
        steps = ["1  Ingest knowledge", "2  Clean & chunk", "3  Retrieve context", "4  Ground response", "5  Show sources"]
        for s in steps:
            ctk.CTkLabel(info, text=s, text_color=MUTED, font=ctk.CTkFont(size=12)).pack(anchor="w", padx=22, pady=7)

    def show_chat(self):
        self.clear()
        self.header("WE Smart Assistant", "Ask about plans and uploaded knowledge. The answer stays bounded by the local sources.")

        outer = self.card(self.content)
        outer.grid(row=1, column=0, sticky="nsew", padx=34, pady=(4, 30))
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(1, weight=1)

        intro = ctk.CTkFrame(outer, fg_color="#F7F3FB", corner_radius=16)
        intro.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        ctk.CTkLabel(
            intro, text="✦  Try:  “What is Nitro Prime 150?”   •   “My budget is 300 EGP”   •   “ايه باقات Tazbeet؟”",
            text_color=PURPLE, font=ctk.CTkFont(size=11, weight="bold")
        ).pack(anchor="w", padx=18, pady=13)

        self.chat_box = ctk.CTkTextbox(
            outer, fg_color="#FCFBFD", text_color=DARK,
            border_width=1, border_color="#EEE7F2",
            corner_radius=16, font=("Segoe UI", 12),
            wrap="word"
        )
        self.chat_box.grid(row=1, column=0, sticky="nsew", padx=20)
        self.chat_box.insert("end", "WE ASSISTANT\nHello 👋 I’m ready. Ask me about WE plans or the loaded knowledge.\n\n")
        self.chat_box.configure(state="disabled")

        bottom = ctk.CTkFrame(outer, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        bottom.grid_columnconfigure(0, weight=1)

        self.chat_entry = ctk.CTkEntry(
            bottom, height=48, corner_radius=14,
            fg_color=DARK, border_width=0,
            text_color="white", placeholder_text_color="#B7AFBF",
            placeholder_text="Type your question in English or Arabic..."
        )
        self.chat_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.chat_entry.bind("<Return>", lambda e: self.send_chat())

        ctk.CTkButton(
            bottom, text="Send", command=self.send_chat,
            width=110, height=48, corner_radius=14,
            fg_color=PURPLE, hover_color=PURPLE2,
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=1)

    def append_chat(self, title, message):
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", f"{title}\n{message}\n\n")
        self.chat_box.see("end")
        self.chat_box.configure(state="disabled")

    def send_chat(self):
        q = self.chat_entry.get().strip()
        if not q:
            return
        self.chat_entry.delete(0, "end")
        self.append_chat("YOU", q)

        result = engine.answer(q)
        answer = result["answer"]
        if result.get("sources"):
            answer += "\n\nSources: " + " • ".join(result["sources"])
        self.append_chat("WE ASSISTANT", answer)

    def show_plans(self):
        self.clear()
        self.header("Plans Explorer", "Browse the structured catalog prepared from official Telecom Egypt plan pages.")

        frame = self.card(self.content)
        frame.grid(row=1, column=0, sticky="nsew", padx=34, pady=(4, 30))
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        filters = ctk.CTkFrame(frame, fg_color="transparent")
        filters.grid(row=0, column=0, sticky="ew", padx=22, pady=(22, 10))
        filters.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(filters, text="Category", text_color=DARK, font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=(0,10))
        categories = ["All"] + sorted({p["category"] for p in engine.plans})
        category = ctk.CTkComboBox(filters, values=categories, width=190, fg_color="#F7F4FA", button_color=PURPLE)
        category.set("All")
        category.grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(filters, text="Maximum price", text_color=DARK, font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=2, padx=(20,10))
        budget = ctk.CTkEntry(filters, width=120, placeholder_text="e.g. 300")
        budget.grid(row=0, column=3)

        columns = ("name","category","price","data","minutes","validity")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=18)
        titles = {"name":"Plan","category":"Category","price":"Price","data":"Data","minutes":"Minutes / Kix","validity":"Validity"}
        for c in columns:
            tree.heading(c, text=titles[c])
        tree.column("name", width=180)
        tree.column("category", width=120)
        tree.column("price", width=90, anchor="center")
        tree.column("data", width=120, anchor="center")
        tree.column("minutes", width=130, anchor="center")
        tree.column("validity", width=110, anchor="center")
        tree.grid(row=2, column=0, sticky="nsew", padx=22, pady=(10,22))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=DARK, fieldbackground="white", rowheight=34, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=PURPLE, foreground="white", relief="flat", font=("Segoe UI", 10, "bold"))

        def refresh():
            for item in tree.get_children():
                tree.delete(item)
            selected = category.get()
            try:
                max_price = float(budget.get()) if budget.get().strip() else None
            except ValueError:
                max_price = None

            for p in engine.plans:
                if selected != "All" and p["category"] != selected:
                    continue
                if max_price is not None and p["price"] > max_price:
                    continue

                data = ""
                if p.get("data_mb") is not None:
                    data = f"{p['data_mb']/1000:g} GB" if p["data_mb"] >= 1000 else f"{p['data_mb']} MB"
                mins = p.get("minutes", p.get("kix", "—"))
                if p.get("kix") is not None:
                    mins = f"{p['kix']} Kix"

                tree.insert("", "end", values=(p["name"], p["category"], f"{p['price']} EGP", data or "—", mins, p.get("validity","—")))

        ctk.CTkButton(
            filters, text="Apply Filter", command=refresh,
            fg_color=PURPLE, hover_color=PURPLE2,
            width=120, height=34, corner_radius=10
        ).grid(row=0, column=4, padx=(12,0))

        refresh()

    def show_upload(self):
        self.clear()
        self.header("Upload Documents", "Extend the local knowledge base with customer or internal reference documents.")

        card = self.card(self.content)
        card.grid(row=1, column=0, sticky="nsew", padx=34, pady=(4, 30))
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            card, text="Drop new knowledge into the assistant",
            text_color=DARK, font=ctk.CTkFont(size=21, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=28, pady=(28, 5))

        ctk.CTkLabel(
            card,
            text="Supported text extraction: PDF, DOCX, TXT, HTML and Markdown. Images can be stored in the workspace; OCR is intentionally not enabled in this lightweight PoC.",
            text_color=MUTED, wraplength=850, justify="left",
            font=ctk.CTkFont(size=11)
        ).grid(row=1, column=0, sticky="w", padx=28, pady=(0, 18))

        box = ctk.CTkTextbox(card, fg_color="#FAF8FC", text_color=DARK, corner_radius=16)
        box.grid(row=2, column=0, sticky="nsew", padx=28)
        box.insert("end", "Current knowledge files:\n\n")
        for row in engine.source_summary():
            box.insert("end", f"• {row['source']}   —   {row['chunks']} chunks\n")
        box.configure(state="disabled")

        def upload():
            files = filedialog.askopenfilenames(
                title="Select documents",
                filetypes=[
                    ("Supported", "*.pdf *.docx *.txt *.html *.htm *.md *.png *.jpg *.jpeg"),
                    ("All files", "*.*")
                ]
            )
            if not files:
                return
            imported = engine.import_files(files)
            messagebox.showinfo("Upload complete", f"{imported} file(s) added and the knowledge index was rebuilt.")
            self.show_upload()

        ctk.CTkButton(
            card, text="＋  Select Documents", command=upload,
            fg_color=PURPLE, hover_color=PURPLE2,
            height=46, corner_radius=14,
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=3, column=0, sticky="w", padx=28, pady=28)

    def show_knowledge(self):
        self.clear()
        self.header("Knowledge Base", "See exactly which local sources are being retrieved by the assistant.")

        card = self.card(self.content)
        card.grid(row=1, column=0, sticky="nsew", padx=34, pady=(4, 30))
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)

        columns = ("source","type","chunks")
        tree = ttk.Treeview(card, columns=columns, show="headings")
        tree.heading("source", text="Source")
        tree.heading("type", text="Type")
        tree.heading("chunks", text="Chunks")
        tree.column("source", width=600)
        tree.column("type", width=140, anchor="center")
        tree.column("chunks", width=120, anchor="center")
        tree.grid(row=0, column=0, sticky="nsew", padx=25, pady=25)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", fieldbackground="white", foreground=DARK, rowheight=36, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=PURPLE, foreground="white", font=("Segoe UI", 10, "bold"))

        for r in engine.source_summary():
            tree.insert("", "end", values=(r["source"], r["type"], r["chunks"]))

    def show_architecture(self):
        self.clear()
        self.header("RAG Architecture", "A simple design that is easy to explain and upgrade to an on-premises production architecture.")

        body = ctk.CTkFrame(self.content, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=34, pady=(4, 30))
        body.grid_columnconfigure((0,1), weight=1)

        items = [
            ("01", "Ingestion", "Official WE plan knowledge + uploaded files."),
            ("02", "Preprocessing", "Clean text and split it into overlapping chunks."),
            ("03", "Retrieval", "Normalize Arabic/English terms and rank relevant chunks."),
            ("04", "Grounding", "Return only retrieved local knowledge and show source names."),
            ("05", "GUI", "CustomTkinter desktop interface with chat, catalog and uploads."),
            ("06", "Upgrade Path", "Replace keyword retrieval with multilingual embeddings + FAISS/Chroma + an on-prem LLM."),
        ]

        for i, (num, title, desc) in enumerate(items):
            c = self.card(body)
            c.grid(row=i//2, column=i%2, sticky="nsew", padx=(0 if i%2==0 else 9, 9 if i%2==0 else 0), pady=9)
            ctk.CTkLabel(c, text=num, text_color=ORANGE, font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=22, pady=(18,4))
            ctk.CTkLabel(c, text=title, text_color=PURPLE, font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=22)
            ctk.CTkLabel(c, text=desc, text_color=MUTED, wraplength=420, justify="left", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=22, pady=(5,20))


if __name__ == "__main__":
    App().mainloop()
