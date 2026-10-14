import os
import streamlit as st
import tts_engine

st.set_page_config(
    page_title="Gerador de Voz Neural Offline",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern styling
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        color: #1E293B;
    }
    .sub-title {
        color: #64748B;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .badge-container {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .badge {
        background-color: #EEF2F6;
        color: #334155;
        border: 1px solid #CBD5E1;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .badge-highlight {
        background-color: #ECFDF5;
        color: #065F46;
        border: 1px solid #A7F3D0;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .result-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.25rem;
        margin-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "history" not in st.session_state:
    st.session_state.history = []

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Configurações de Voz")

    voice_options = list(tts_engine.VOICES.keys())

    def format_voice_label(key):
        v = tts_engine.VOICES[key]
        status = "✅ Pronta" if tts_engine.is_model_downloaded(key) else "⬇️ Baixar"
        return f"{v['label']} [{status}]"

    # Default to dii if available
    default_idx = voice_options.index("dii") if "dii" in voice_options else 0
    selected_voice_key = st.selectbox(
        "Selecione o Modelo de Voz:",
        voice_options,
        index=default_idx,
        format_func=format_voice_label,
    )

    selected_voice_info = tts_engine.VOICES[selected_voice_key]
    is_ready = tts_engine.is_model_downloaded(selected_voice_key)

    st.markdown(
        f"""
        **Detalhes da Voz Selecionada:**
        - **Gênero:** {selected_voice_info['gender']}
        - **Fidelidade:** {selected_voice_info['quality']}
        - **Status:** {'Disponível localmente' if is_ready else 'Requer download (~64 MB)'}
        """
    )

    if not is_ready:
        if st.button("⬇️ Baixar esta voz agora", use_container_width=True):
            progress_bar = st.progress(0, text="Iniciando download...")

            def progress_callback(pct, text):
                progress_bar.progress(pct, text=text)

            with st.spinner("Baixando e extraindo modelo..."):
                tts_engine.download_model(selected_voice_key, progress_callback=progress_callback)
            st.success("Voz instalada com sucesso!")
            st.rerun()

    st.divider()

    st.subheader("🎛️ Parâmetros da Fala")
    speed = st.slider(
        "Velocidade de reprodução:",
        min_value=0.6,
        max_value=1.6,
        value=1.0,
        step=0.05,
        help="Valores maiores aceleram a fala. 1.0 é a velocidade natural.",
    )

    num_threads = st.slider(
        "Núcleos de CPU (Threads):",
        min_value=1,
        max_value=8,
        value=4,
        step=1,
        help="Quantidade de núcleos do processador dedicados à síntese neural.",
    )

    st.divider()
    st.markdown(
        """
        **💡 Sobre o Sistema:**
        - **Motor:** Sherpa-ONNX (VITS / Piper Neural)
        - **Modo:** 100% Offline / Local (Privacidade Total)
        - **Consumo:** Otimizado para CPU Intel
        """
    )

# Main Area
st.markdown("<div class='main-title'>🎙️ Conversor de Texto em Voz (Offline)</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='sub-title'>Geração de áudio com síntese neural de alta qualidade em português (pt-BR) rodando direto no seu computador.</div>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class='badge-container'>
        <span class='badge-highlight'>🔒 100% Offline & Seguro</span>
        <span class='badge'>⚡ Alta Velocidade no CPU</span>
        <span class='badge'>🇧🇷 Português Brasileiro Nativo</span>
        <span class='badge'>🆓 Sem Custos ou Limites de API</span>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_text, tab_file = st.tabs(["✍️ Digitar / Colar Texto", "📄 Carregar Arquivo de Texto"])

sample_texts = {
    "Personalizado": "",
    "Boas-vindas": "Olá! Seja muito bem-vindo ao sistema de conversão de texto para voz. Este áudio está sendo gerado totalmente no seu próprio computador, com qualidade neural e sem gastar conexão de internet.",
    "Notícia / Informativo": "A inteligência artificial aplicada ao processamento de linguagem natural e áudio atingiu um novo patamar. Hoje é possível rodar modelos de redes neurais complexos diretamente no processador doméstico com altíssima fidelidade e baixo consumo de energia.",
    "Narrativa / História": "Era uma manhã tranquila quando as primeiras luzes do sol tocaram a janela. O silêncio da casa foi quebrado apenas pelo canto dos pássaros no jardim.",
}

input_text = ""

with tab_text:
    col_preset, _ = st.columns([1, 2])
    with col_preset:
        preset_choice = st.selectbox("Carregar texto de exemplo:", list(sample_texts.keys()))

    default_value = sample_texts[preset_choice] if preset_choice != "Personalizado" else ""
    user_text = st.text_area(
        "Insira o texto que você deseja transformar em fala:",
        value=default_value,
        height=180,
        placeholder="Digite ou cole aqui o seu texto em português...",
    )
    input_text = user_text

with tab_file:
    uploaded_file = st.file_uploader("Faça upload de um arquivo .txt:", type=["txt"])
    if uploaded_file is not None:
        try:
            file_content = uploaded_file.read().decode("utf-8")
            st.text_area("Pré-visualização do arquivo:", value=file_content, height=180, disabled=True)
            input_text = file_content
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            file_content = uploaded_file.read().decode("latin-1")
            st.text_area("Pré-visualização do arquivo:", value=file_content, height=180, disabled=True)
            input_text = file_content

col_stats1, col_stats2, col_stats3 = st.columns(3)
char_count = len(input_text.strip())
word_count = len(input_text.strip().split()) if char_count > 0 else 0
estimated_secs = max(1, round(word_count / 2.5)) if word_count > 0 else 0

with col_stats1:
    st.caption(f"📝 **Caracteres:** {char_count}")
with col_stats2:
    st.caption(f"📖 **Palavras:** {word_count}")
with col_stats3:
    st.caption(f"⏱️ **Duração estimada:** ~{estimated_secs}s")

col_btn, _ = st.columns([1, 2])
with col_btn:
    generate_clicked = st.button("🎙️ Gerar Áudio", type="primary", use_container_width=True)

if generate_clicked:
    if not input_text.strip():
        st.warning("Por favor, digite ou selecione um texto antes de gerar o áudio.")
    else:
        progress_placeholder = st.empty()
        with st.spinner(f"Sintetizando fala com a voz '{selected_voice_info['label']}'..."):
            try:
                def on_progress(pct, msg):
                    progress_placeholder.progress(pct, text=msg)

                result = tts_engine.synthesize_text(
                    text=input_text,
                    voice_key=selected_voice_key,
                    speed=speed,
                    num_threads=num_threads,
                    progress_callback=on_progress,
                )
                progress_placeholder.empty()

                st.success("✅ Áudio gerado com sucesso!")

                # Audio Player & Details
                st.audio(result["audio_bytes"], format="audio/wav")

                col_d1, col_d2, col_d3, col_dl = st.columns([1, 1, 1, 1.5])
                with col_d1:
                    st.metric("Duração do Áudio", f"{result['duration_seconds']:.2f}s")
                with col_d2:
                    st.metric("Tempo de Geração", f"{result['elapsed_seconds']:.2f}s")
                with col_d3:
                    rt_speed = result["duration_seconds"] / max(result["elapsed_seconds"], 0.001)
                    st.metric("Velocidade", f"{rt_speed:.1f}x real-time")
                with col_dl:
                    st.download_button(
                        label="⬇️ Baixar Arquivo WAV",
                        data=result["audio_bytes"],
                        file_name=result["filename"],
                        mime="audio/wav",
                        use_container_width=True,
                    )

                # Save to history
                st.session_state.history.insert(
                    0,
                    {
                        "filename": result["filename"],
                        "voice": selected_voice_info["label"],
                        "text": input_text[:80] + ("..." if len(input_text) > 80 else ""),
                        "duration": f"{result['duration_seconds']:.2f}s",
                        "audio_bytes": result["audio_bytes"],
                    },
                )
            except Exception as e:
                progress_placeholder.empty()
                st.error(f"Erro ao gerar áudio: {str(e)}")

# Session History
if st.session_state.history:
    st.divider()
    st.subheader("📜 Histórico de Áudios Gerados nesta Sessão")

    for i, item in enumerate(st.session_state.history):
        with st.expander(f"🔊 {item['voice']} - \"{item['text']}\" ({item['duration']})", expanded=(i == 0)):
            st.audio(item["audio_bytes"], format="audio/wav")
            st.download_button(
                label=f"⬇️ Baixar {item['filename']}",
                data=item["audio_bytes"],
                file_name=item["filename"],
                mime="audio/wav",
                key=f"hist_dl_{i}",
            )
