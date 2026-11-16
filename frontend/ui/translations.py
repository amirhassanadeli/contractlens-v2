TEXTS = {
    "fa": {
        "subtitle": "دستیار بررسی قراردادها",
        "notice": (
            "PDF به Django ارسال می‌شود و پاسخ از سرویس RAG دریافت می‌شود. "
            "نسخه توسعه؛ فایل حساس بارگذاری نکنید."
        ),
        "select_contract": "انتخاب قرارداد",
        "source": "کدام فایل را استفاده کنیم؟",
        "english_pdf": "PDF انگلیسی پیش‌فرض",
        "persian_pdf": "PDF فارسی پیش‌فرض",
        "upload_pdf": "آپلود PDF خودم",
        "upload_label": "فایل PDF را انتخاب کنید",
        "upload_help": "حداکثر ۵ مگابایت و ۳۰ صفحه",
        "reading": "در حال خواندن PDF...",
        "ready": "فایل آماده است: {name}",
        "missing_file": "فایل پیش‌فرض در پوشه samples پیدا نشد.",
        "invalid_pdf": "خواندن PDF ناموفق بود؛ سالم‌بودن فایل را بررسی کنید.",
        "empty_file": "فایل خالی است.",
        "large_file": "حجم فایل نباید بیشتر از ۵ مگابایت باشد.",
        "encrypted": "PDF رمزگذاری‌شده پشتیبانی نمی‌شود.",
        "many_pages": "PDF باید حداکثر ۳۰ صفحه باشد.",
        "long_text": "متن PDF باید حداکثر ۳۰ هزار نویسه باشد.",
        "no_text": "متنی استخراج نشد؛ PDF اسکن‌شده به OCR نیاز دارد.",
        "clear": "🗑️ پاک‌کردن گفتگو",
        "history_note": (
            "پاک‌کردن یا تغییر قرارداد، گفت‌وگوی جدیدی شروع می‌کند؛ "
            "گفت‌وگوهای قبلی از دیتابیس حذف نمی‌شوند."
        ),
        "title": "💬 گفت‌وگو با ContractLens",
        "active": "قرارداد فعال: {name}",
        "choose_first": "ابتدا یک PDF معتبر از نوار کناری انتخاب کنید.",
        "welcome": (
            "سلام! یک قرارداد PDF انتخاب کنید و درباره آن سؤال بپرسید. "
            "پاسخ‌ها را با متن اصلی قرارداد بررسی کنید."
        ),
        "prompt": "درباره قرارداد سؤال بپرسید...",
        "waiting": "در حال دریافت پاسخ از Django...",
        "timeout": "زمان انتظار برای پاسخ تمام شد.",
        "connection": "اتصال به Django برقرار نشد؛ روشن‌بودن سرور را بررسی کنید.",
        "http_error": "بک‌اند خطای HTTP {status} برگرداند.",
        "request_error": "در ارسال درخواست خطایی رخ داد.",
        "response_error": "پاسخ بک‌اند قالب معتبری ندارد.",
        "retry_note": "درخواست ممکن است در سرور ثبت شده باشد؛ تلاش مجدد می‌تواند پیام یا قرارداد تکراری بسازد.",
        "like": "👍 لایک",
        "dislike": "👎 دیس‌لایک",
        "regenerate": "🔄 تولید مجدد",
        "saving": "در حال ثبت بازخورد...",
        "regenerating": "در حال تولید پاسخ جدید...",
        "legacy_message": "برای فعال‌شدن دکمه‌ها، یک سؤال جدید بفرستید؛ شناسه این پاسخ در رابط ذخیره نشده است.",
        "retry": "تلاش مجدد",
    },

    "en": {
        "subtitle": "Contract review assistant",
        "notice": (
            "PDFs are uploaded to Django for RAG processing. "
            "Development only: do not upload sensitive files."
        ),
        "select_contract": "Select a contract",
        "source": "Which file would you like to use?",
        "english_pdf": "Default English PDF",
        "persian_pdf": "Default Persian PDF",
        "upload_pdf": "Upload my PDF",
        "upload_label": "Choose a PDF file",
        "upload_help": "Up to 5 MB and 30 pages",
        "reading": "Reading PDF...",
        "ready": "File ready: {name}",
        "missing_file": "The default file was not found in the samples folder.",
        "invalid_pdf": "Could not read the PDF. Check that the file is valid.",
        "empty_file": "The file is empty.",
        "large_file": "The file must not exceed 5 MB.",
        "encrypted": "Encrypted PDFs are not supported.",
        "many_pages": "The PDF must contain no more than 30 pages.",
        "long_text": "PDF text must not exceed 30,000 characters.",
        "no_text": "No text was extracted. Scanned PDFs require OCR.",
        "clear": "🗑️ Clear conversation",
        "history_note": (
            "Clearing or changing the contract starts a new conversation. "
            "Previous conversations are not deleted from the database."
        ),
        "title": "💬 Chat with ContractLens",
        "active": "Active contract: {name}",
        "choose_first": "Select a valid PDF from the sidebar first.",
        "welcome": (
            "Hello! Select a PDF contract and ask a question about it. "
            "Check answers against the original contract."
        ),
        "prompt": "Ask a question about the contract...",
        "waiting": "Waiting for Django...",
        "timeout": "The request timed out.",
        "connection": "Could not connect to Django. Check that the server is running.",
        "http_error": "The backend returned HTTP {status}.",
        "request_error": "The request could not be sent.",
        "response_error": "The backend returned an invalid response.",
        "retry_note": "The server may have saved the request. Retrying may create duplicate messages or contracts.",
        "like": "👍 Like",
        "dislike": "👎 Dislike",
        "regenerate": "🔄 Regenerate",
        "saving": "Saving feedback...",
        "regenerating": "Generating a new response...",
        "legacy_message": "Send a new question to enable actions; this response has no saved ID in the UI.",
        "retry": "Try again",
    },
}
