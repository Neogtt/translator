import json
import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


def build_prompt(customer_message: str, user_reply_turkish: str, tone: str) -> str:
    return f"""
You are a multilingual customer support assistant.

Task:
1) Detect the language of the customer's message.
2) Translate the customer message into Turkish.
3) Provide a short Turkish summary.
4) If a Turkish draft reply is provided, improve it so it is clear and professional.
5) If no draft is provided, create a suitable Turkish reply from scratch.
6) Translate the final Turkish reply into the customer's original language in the selected tone.

Tone options:
- formal
- informal
- neutral

Selected tone: {tone}

Return ONLY valid JSON with this schema:
{{
  "detected_language": "string",
  "customer_message_tr": "string",
  "summary_tr": "string",
  "reply_tr_improved": "string",
  "reply_in_customer_language": "string"
}}

Customer message:
\"\"\"{customer_message}\"\"\"

Draft reply in Turkish:
\"\"\"{user_reply_turkish}\"\"\"
"""


def get_api_key() -> str:
    secret_key = st.secrets.get("OPENAI_API_KEY", "")
    env_key = os.getenv("OPENAI_API_KEY", "")
    return (secret_key or env_key).strip()


def ask_ai(api_key: str, customer_message: str, user_reply_turkish: str, tone: str) -> dict:
    client = OpenAI(api_key=api_key)
    prompt = build_prompt(customer_message, user_reply_turkish, tone)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You generate precise business communication outputs."},
            {"role": "user", "content": prompt},
        ],
    )

    content = response.choices[0].message.content or "{}"
    return json.loads(content)


def main() -> None:
    st.set_page_config(page_title="Cheviri AI", page_icon="💬", layout="centered")
    st.title("Cheviri AI")
    st.caption("Yabancı dilde müşteri mesajlarını anla, Türkçe cevap hazırla, otomatik geri çevir.")

    st.info("API key Streamlit secrets/.env'den okunur. Ekranda key girmen gerekmez.")
    api_key = get_api_key()

    tone = st.selectbox(
        "Yanıt tonu",
        options=["formal", "neutral", "informal"],
        index=0,
    )

    customer_message = st.text_area(
        "Müşteriden gelen mesaj",
        placeholder="Örn: Hello, I did not receive my order yet. Can you help?",
        height=140,
    )

    user_reply_turkish = st.text_area(
        "Senin Türkçe cevap taslağın (opsiyonel)",
        placeholder="Boş bırakabilirsin. Dilersen taslak yaz: Merhaba, yaşadığınız gecikme için üzgünüz...",
        height=140,
    )

    run_btn = st.button("Çevir ve Cevap Üret", type="primary")

    if run_btn:
        if not api_key:
            st.error("OPENAI_API_KEY bulunamadı. Streamlit Secrets veya .env içine ekleyin.")
        elif not customer_message.strip():
            st.error("Lütfen müşteriden gelen mesajı yazın.")
        else:
            with st.spinner("AI yanıt oluşturuyor..."):
                try:
                    result = ask_ai(
                        api_key=api_key.strip(),
                        customer_message=customer_message.strip(),
                        user_reply_turkish=user_reply_turkish.strip(),
                        tone=tone,
                    )

                    st.success("Hazır.")
                    st.subheader("Dil Tespiti")
                    st.write(result.get("detected_language", "-"))

                    st.subheader("Müşteri Mesajı (Türkçe)")
                    st.write(result.get("customer_message_tr", "-"))

                    st.subheader("Kısa Özet (TR)")
                    st.write(result.get("summary_tr", "-"))

                    st.subheader("Geliştirilmiş Cevap (TR)")
                    st.write(result.get("reply_tr_improved", "-"))

                    st.subheader("Müşteri Dilinde Gönderilecek Cevap")
                    st.code(result.get("reply_in_customer_language", "-"), language=None)

                except Exception as exc:
                    st.error(f"Hata oluştu: {exc}")


if __name__ == "__main__":
    main()
