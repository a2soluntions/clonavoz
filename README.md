# 🎙️ Clonavoz AI • Gerador & Clonagem de Voz Neural Offline

Sistema moderno e ultra-rápido de conversão de texto em fala (Text-to-Speech) em português do Brasil (pt-BR), com **suporte a vozes femininas e masculinas, upload de áudio de referência para clonagem de voz**, visualizador interativo de ondas sonoras (WaveSurfer) e processamento **100% local e offline**.

---

## ✨ Principais Funcionalidades

- **Seletor de Vozes em Dropdown (Select Box):**
  - Caixa de seleção compacta e moderna, agrupada por:
    - ⭐ **Minhas Vozes Customizadas / Clonadas**
    - 👩 **Vozes Femininas (Padrão)**
    - 👨 **Vozes Masculinas (Padrão)**
  - Badges dinâmicos de status (Instalada, Requer Download, Voz Clonada).
  - Botão integrado para ouvir a amostra de referência original da voz enviada.
  - Botão para exclusão de vozes customizadas.
- **Upload de Vozes & Decodificação Universal (PyAV):**
  - Aceita qualquer formato de áudio: `.wav`, `.mp3`, `.m4a`, `.aac`, `.ogg`, `.flac`.
  - Converte e normaliza automaticamente para padrão mono 22050Hz.
  - Análise acústica com estimativa de frequência fundamental ($F_0$ em Hertz) e transposição semitonal.
- **Síntese Neural Adaptativa:**
  - Aplica o perfil de tom e pitch da voz enviada sobre a base neural local.
- **Visualizador de Ondas Sonoras (WaveSurfer.js):**
  - Navegação por clique na onda sonora e contador em tempo real.
- **Editor Completo com Drag & Drop de `.txt`**

---

## 🚀 Como Executar

Dê um duplo clique no arquivo:
```
run.bat
```
O navegador abrirá automaticamente em:
👉 **`http://localhost:8000`**
