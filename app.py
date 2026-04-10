import json
import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


def build_analyze_prompt(customer_message: str) -> str:
    return f"""
You are a multilingual customer support assistant.

Task:
1) Detect the language of the customer's message.
2) Translate the customer message into Turkish.
3) Provide a short Turkish summary.

Return ONLY valid JSON with this schema:
{{
  "detected_language": "string",
  "customer_message_tr": "string",
  "summary_tr": "string"
}}

Customer message:
\"\"\"{customer_message}\"\"\"
"""


def build_reply_prompt(
    customer_message: str,
    customer_message_tr: str,
    user_reply_turkish: str,
    tone: str,
) -> str:
    return f"""
You are a multilingual customer support assistant.

Task:
1) Use the original customer message and Turkish translation context.
2) If a Turkish draft reply is provided, improve it professionally.
3) If no draft is provided, create a suitable Turkish customer reply from scratch.
4) Translate the final Turkish reply into the customer's original language.
5) Apply this tone: {tone}.

Return ONLY valid JSON with this schema:
{{
  "reply_tr_final": "string",
  "reply_in_customer_language": "string"
}}

Original customer message:
\"\"\"{customer_message}\"\"\"

Customer message in Turkish:
\"\"\"{customer_message_tr}\"\"\"

Draft reply in Turkish (optional):
\"\"\"{user_reply_turkish}\"\"\"
"""


def get_api_key() -> str:
    secret_key = st.secrets.get("OPENAI_API_KEY", "")
    env_key = os.getenv("OPENAI_API_KEY", "")
    return (secret_key or env_key).strip()


def ask_ai(api_key: str, prompt: str) -> dict:
    client = OpenAI(api_key=api_key)

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
        "Yanıt tonu (cevap üretiminde kullanılır)",
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

    translate_btn = st.button("1) Önce Çevir", type="primary")
    generate_btn = st.button("2) Sonra Cevap Üret")

    if translate_btn:
        if not api_key:
            st.error("OPENAI_API_KEY bulunamadı. Streamlit Secrets veya .env içine ekleyin.")
        elif not customer_message.strip():
            st.error("Lütfen müşteriden gelen mesajı yazın.")
        else:
            with st.spinner("Mesaj çevriliyor..."):
                try:
                    analysis = ask_ai(api_key=api_key.strip(), prompt=build_analyze_prompt(customer_message.strip()))
                    st.session_state["analysis"] = analysis
                    st.session_state["last_customer_message"] = customer_message.strip()
                    st.session_state.pop("reply", None)
                    st.success("Çeviri tamamlandı.")

                except Exception as exc:
                    st.error(f"Hata oluştu: {exc}")

    analysis = st.session_state.get("analysis")
    if analysis:
        st.subheader("Dil Tespiti")
        st.write(analysis.get("detected_language", "-"))

        st.subheader("Müşteri Mesajı (Türkçe)")
        st.write(analysis.get("customer_message_tr", "-"))

        st.subheader("Kısa Özet (TR)")
        st.write(analysis.get("summary_tr", "-"))

    if generate_btn:
        if not api_key:
            st.error("OPENAI_API_KEY bulunamadı. Streamlit Secrets veya .env içine ekleyin.")
        elif not customer_message.strip():
            st.error("Lütfen müşteriden gelen mesajı yazın.")
        elif not analysis or st.session_state.get("last_customer_message") != customer_message.strip():
            st.error("Önce güncel mesaj için '1) Önce Çevir' butonuna basın.")
        else:
            with st.spinner("Cevap oluşturuluyor..."):
                try:
                    reply = ask_ai(
                        api_key=api_key.strip(),
                        prompt=build_reply_prompt(
                            customer_message=customer_message.strip(),
                            customer_message_tr=analysis.get("customer_message_tr", ""),
                            user_reply_turkish=user_reply_turkish.strip(),
                            tone=tone,
                        ),
                    )
                    st.session_state["reply"] = reply
                    st.success("Cevap hazır.")
                except Exception as exc:
                    st.error(f"Hata oluştu: {exc}")

    reply = st.session_state.get("reply")
    if reply:
        st.subheader("Müşteri Dilinde Gönderilecek Cevap")
        st.code(reply.get("reply_in_customer_language", "-"), language=None)

        st.subheader("Türkçe Karşılığı")
        st.write(reply.get("reply_tr_final", "-"))


if __name__ == "__main__":
    main()
