from pathlib import Path
from collections import defaultdict
import json
import re
import shutil

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

try:
    from docx import Document
except Exception:
    Document = None


class RAGEngine:

    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)

        self.knowledge_dir = self.base_dir / "knowledge"
        self.knowledge_dir.mkdir(exist_ok=True)

        self.plans_file = self.base_dir / "plans.json"

        self.chunks = []
        self.plans = []

        self.reload()

    # =====================================================
    # CLEANING
    # =====================================================

    def clean(self, text):
        return re.sub(r"\s+", " ", text or "").strip()

    def normalize(self, text):
        text = (text or "").lower()

        replacements = {
            "النت": "انترنت",
            "نت": "انترنت",
            "باقه": "باقة",
            "باقات": "باقة",
            "كام": "سعر",
            "فلوس": "سعر",
            "جيجا": "gb",
            "جيجابايت": "gb",
            "دقايق": "minutes",
            "دقيقة": "minutes",
            "ميجا": "mb",
            "ميجابايت": "mb",
            "وي جولد": "we gold",
            "وي ميكس": "we mix",
            "سوبر كيكس": "super kix",
            "تظبيط": "tazbeet",
            "نيترو برايم": "nitro prime",
            "نيترو ميفاي": "nitro mifi"
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text

    def _is_arabic(self, text):
        return bool(
            re.search(
                r"[\u0600-\u06FF]",
                text or ""
            )
        )

    def tokens(self, text):
        return set(
            re.findall(
                r"[\w\u0600-\u06FF]+",
                self.normalize(text)
            )
        )

    # =====================================================
    # CHUNKING
    # =====================================================

    def chunk_text(self, text, size=650, overlap=100):
        text = self.clean(text)

        if not text:
            return []

        result = []
        start = 0

        while start < len(text):
            end = start + size

            result.append(
                text[start:end]
            )

            start = max(
                end - overlap,
                start + 1
            )

        return result

    # =====================================================
    # FILE READING
    # =====================================================

    def read_file(self, path):
        ext = path.suffix.lower()

        if ext in {
            ".txt",
            ".md",
            ".html",
            ".htm"
        }:
            return path.read_text(
                encoding="utf-8",
                errors="ignore"
            )

        if ext == ".pdf" and PdfReader:
            reader = PdfReader(str(path))

            return "\n".join(
                (page.extract_text() or "")
                for page in reader.pages
            )

        if ext == ".docx" and Document:
            doc = Document(str(path))

            return "\n".join(
                paragraph.text
                for paragraph in doc.paragraphs
            )

        return ""

    # =====================================================
    # LOAD DATA
    # =====================================================

    def reload(self):
        self.chunks = []

        if self.plans_file.exists():
            try:
                self.plans = json.loads(
                    self.plans_file.read_text(
                        encoding="utf-8"
                    )
                )
            except Exception:
                self.plans = []
        else:
            self.plans = []

        if not self.knowledge_dir.exists():
            return

        for path in self.knowledge_dir.iterdir():

            if not path.is_file():
                continue

            text = self.read_file(path)

            for i, chunk in enumerate(
                self.chunk_text(text)
            ):

                self.chunks.append(
                    {
                        "source": path.name,
                        "chunk_id": i,
                        "type": (
                            path.suffix
                            .lower()
                            .lstrip(".")
                            .upper()
                        ),
                        "text": chunk
                    }
                )

    # =====================================================
    # RETRIEVAL
    # =====================================================

    def retrieve(self, query, top_k=4):
        query_tokens = self.tokens(query)

        scored = []

        for item in self.chunks:

            chunk_tokens = self.tokens(
                item["text"]
            )

            score = len(
                query_tokens.intersection(
                    chunk_tokens
                )
            )

            if score > 0:
                scored.append(
                    (
                        score,
                        item
                    )
                )

        scored.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return [
            item
            for _, item in scored[:top_k]
        ]

    # =====================================================
    # NUMBERS
    # =====================================================

    def _numbers(self, text):
        return [
            float(x)
            for x in re.findall(
                r"\d+(?:\.\d+)?",
                text
            )
        ]

    # =====================================================
    # FORMAT PLAN
    # =====================================================

    def describe_plan(
        self,
        plan,
        lead,
        arabic=True
    ):

        if arabic:
            lines = [
                f"{lead} {plan['name']} "
                f"بسعر {plan['price']} EGP."
            ]
        else:
            lines = [
                f"{lead} {plan['name']} "
                f"for {plan['price']} EGP."
            ]

        if plan.get("data_mb") is not None:
            mb = plan["data_mb"]

            if mb >= 1000:
                data = f"{mb / 1000:g} GB"
            else:
                data = f"{mb:g} MB"

            lines.append(
                f"🌐 الإنترنت: {data}"
                if arabic
                else f"🌐 Data: {data}"
            )

        if plan.get("minutes") is not None:
            lines.append(
                f"📞 الدقائق: {plan['minutes']}"
                if arabic
                else f"📞 Minutes: {plan['minutes']}"
            )

        if plan.get("sms") is not None:
            lines.append(
                f"💬 SMS: {plan['sms']}"
            )

        if plan.get("kix") is not None:
            lines.append(
                f"📦 Kix: {plan['kix']}"
            )

        if plan.get("validity"):
            lines.append(
                f"⏱️ الصلاحية: {plan['validity']}"
                if arabic
                else f"⏱️ Validity: {plan['validity']}"
            )

        return "\n".join(lines)

    # =====================================================
    # SMART PLAN LOGIC
    # =====================================================

    def _plan_answer(self, query):
        q = self.normalize(query)
        nums = self._numbers(q)

        if not self.plans:
            return None

        arabic = self._is_arabic(query)

        # -------------------------------------------------
        # 1) BUDGET / SMART PLAN
        # -------------------------------------------------

        budget_words = [
            "budget",
            "under",
            "ميزاني",
            "معايا",
            "معي",
            "عندي",
            "جنيه",
            "egp",
            "سعر"
        ]

        only_number = bool(
            re.fullmatch(
                r"\s*\d+(?:\.\d+)?\s*",
                query
            )
        )

        is_budget = (
            bool(nums)
            and (
                only_number
                or any(
                    word in q
                    for word in budget_words
                )
            )
        )

        if is_budget:
            budget = nums[0]

            eligible = [
                p
                for p in self.plans
                if p.get(
                    "price",
                    999999
                ) <= budget
            ]

            if not eligible:

                if arabic:
                    answer = (
                        f"ميزانيتك {budget:g} EGP، "
                        "ومفيش باقة متاحة أقل من الميزانية دي."
                    )
                else:
                    answer = (
                        f"Your budget is {budget:g} EGP, "
                        "but there is no available plan below this budget."
                    )

                return {
                    "answer": answer,
                    "sources": ["plans.json"]
                }

            best = max(
                eligible,
                key=lambda p: p.get(
                    "price",
                    0
                )
            )

            saving = budget - best["price"]

            if arabic:
                answer = (
                    f"💰 معاك {budget:g} EGP.\n\n"
                    f"أنسب باقة ليك هي {best['name']} "
                    f"بسعر {best['price']} EGP.\n"
                )

                if saving > 0:
                    answer += (
                        f"✅ هتوفر {saving:g} EGP.\n\n"
                    )
                else:
                    answer += (
                        "✅ الباقة مناسبة لميزانيتك بالظبط.\n\n"
                    )

            else:
                answer = (
                    f"💰 Your budget is {budget:g} EGP.\n\n"
                    f"The closest plan within your budget is "
                    f"{best['name']} for {best['price']} EGP.\n"
                )

                if saving > 0:
                    answer += (
                        f"✅ You will save {saving:g} EGP.\n\n"
                    )
                else:
                    answer += (
                        "✅ This plan exactly matches your budget.\n\n"
                    )

            if best.get("data_mb") is not None:
                mb = best["data_mb"]

                if mb >= 1000:
                    data = f"{mb / 1000:g} GB"
                else:
                    data = f"{mb:g} MB"

                answer += (
                    f"🌐 الإنترنت: {data}\n"
                    if arabic
                    else f"🌐 Data: {data}\n"
                )

            if best.get("minutes") is not None:
                answer += (
                    f"📞 الدقائق: {best['minutes']}\n"
                    if arabic
                    else f"📞 Minutes: {best['minutes']}\n"
                )

            if best.get("sms") is not None:
                answer += (
                    f"💬 SMS: {best['sms']}\n"
                )

            if best.get("kix") is not None:
                answer += (
                    f"📦 Kix: {best['kix']}\n"
                )

            if best.get("validity"):
                answer += (
                    f"⏱️ الصلاحية: {best['validity']}"
                    if arabic
                    else f"⏱️ Validity: {best['validity']}"
                )

            return {
                "answer": answer,
                "sources": [
                    best.get(
                        "source",
                        "plans.json"
                    )
                ]
            }

        # -------------------------------------------------
        # 2) CHEAPEST
        # -------------------------------------------------

        if (
            "cheapest" in q
            or "ارخص" in q
        ):

            best = min(
                self.plans,
                key=lambda p: p.get(
                    "price",
                    999999
                )
            )

            lead = (
                "أرخص باقة متاحة هي"
                if arabic
                else "The cheapest available plan is"
            )

            return {
                "answer": self.describe_plan(
                    best,
                    lead,
                    arabic
                ),
                "sources": [
                    best.get(
                        "source",
                        "plans.json"
                    )
                ]
            }

        # -------------------------------------------------
        # 3) CATEGORY SEARCH
        # -------------------------------------------------

        categories = [
            "we gold",
            "nitro prime",
            "nitro mifi",
            "super kix",
            "tazbeet",
            "we mix"
        ]

        for category in categories:

            if category in q:

                subset = [
                    p
                    for p in self.plans
                    if (
                        p.get(
                            "category",
                            ""
                        ).lower()
                        == category
                    )
                ]

                if not subset:
                    continue

                # Name + exact price
                if nums:

                    requested_price = nums[-1]

                    exact = [
                        p
                        for p in subset
                        if p.get(
                            "price"
                        ) == requested_price
                    ]

                    if exact:
                        plan = exact[0]

                        lead = (
                            "تفاصيل الباقة"
                            if arabic
                            else "Plan details:"
                        )

                        return {
                            "answer": self.describe_plan(
                                plan,
                                lead,
                                arabic
                            ),
                            "sources": [
                                plan.get(
                                    "source",
                                    "plans.json"
                                )
                            ]
                        }

                # Category only -> show all plans
                if arabic:
                    answer = (
                        f"الباقات المتاحة في "
                        f"{subset[0]['category']}:\n\n"
                    )
                else:
                    answer = (
                        f"Available "
                        f"{subset[0]['category']} plans:\n\n"
                    )

                for plan in sorted(
                    subset,
                    key=lambda p: p.get(
                        "price",
                        0
                    )
                ):

                    answer += (
                        f"• {plan['name']} - "
                        f"{plan['price']} EGP"
                    )

                    details = []

                    if plan.get("data_mb") is not None:
                        mb = plan["data_mb"]

                        if mb >= 1000:
                            data = (
                                f"{mb / 1000:g} GB"
                            )
                        else:
                            data = (
                                f"{mb:g} MB"
                            )

                        details.append(
                            f"الإنترنت: {data}"
                            if arabic
                            else f"Data: {data}"
                        )

                    if plan.get("minutes") is not None:
                        details.append(
                            f"الدقائق: {plan['minutes']}"
                            if arabic
                            else f"Minutes: {plan['minutes']}"
                        )

                    if plan.get("sms") is not None:
                        details.append(
                            f"SMS: {plan['sms']}"
                        )

                    if plan.get("kix") is not None:
                        details.append(
                            f"Kix: {plan['kix']}"
                        )

                    if plan.get("validity"):
                        details.append(
                            f"الصلاحية: {plan['validity']}"
                            if arabic
                            else f"Validity: {plan['validity']}"
                        )

                    if details:
                        answer += (
                            "\n  "
                            + " | ".join(details)
                        )

                    answer += "\n\n"

                return {
                    "answer": answer.strip(),
                    "sources": list(
                        {
                            p.get(
                                "source",
                                "plans.json"
                            )
                            for p in subset
                        }
                    )
                }

        return None

    # =====================================================
    # MAIN ANSWER
    # =====================================================

    def answer(self, query):

        plan_result = self._plan_answer(
            query
        )

        if plan_result:
            return plan_result

        results = self.retrieve(
            query
        )

        if not results:
            arabic = self._is_arabic(
                query
            )

            return {
                "answer": (
                    "مش لاقي إجابة كافية في البيانات الحالية."
                    if arabic
                    else
                    "I could not find enough information in the current knowledge base."
                ),
                "sources": []
            }

        best = results[0]["text"]

        if len(best) > 650:
            best = (
                best[:650]
                .rstrip()
                + "..."
            )

        sources = []

        for item in results:
            source = item["source"]

            if source not in sources:
                sources.append(
                    source
                )

        return {
            "answer": best,
            "sources": sources
        }

    # =====================================================
    # IMPORT FILES
    # =====================================================

    def import_files(self, files):

        allowed = {
            ".pdf",
            ".docx",
            ".txt",
            ".html",
            ".htm",
            ".md",
            ".png",
            ".jpg",
            ".jpeg"
        }

        imported = 0

        for file_name in files:

            source = Path(
                file_name
            )

            if (
                source.suffix.lower()
                not in allowed
            ):
                continue

            destination = (
                self.knowledge_dir
                / source.name
            )

            number = 2

            while destination.exists():

                destination = (
                    self.knowledge_dir
                    / (
                        source.stem
                        + "_"
                        + str(number)
                        + source.suffix
                    )
                )

                number += 1

            shutil.copy2(
                source,
                destination
            )

            imported += 1

        self.reload()

        return imported

    # =====================================================
    # HELPERS FOR GUI
    # =====================================================

    def chunk_count(self):
        return len(
            self.chunks
        )

    def source_summary(self):

        counts = defaultdict(
            int
        )

        types = {}

        for item in self.chunks:

            source = item[
                "source"
            ]

            counts[source] += 1

            types[source] = item[
                "type"
            ]

        rows = []

        for source in sorted(
            counts
        ):

            rows.append(
                {
                    "source": source,
                    "chunks": counts[source],
                    "type": types[source]
                }
            )

        return rows