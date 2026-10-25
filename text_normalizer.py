"""
VOXSTUDIO / CLONAVOZ - Módulo de Normalização Gramatical e Fonética PT-BR
Garante dicção perfeita, pontuação respiratória e expansão de abreviações e moedas.
"""

import re

UNITS = ['', 'um', 'dois', 'três', 'quatro', 'cinco', 'seis', 'sete', 'oito', 'nove']
TEENS = ['dez', 'onze', 'doze', 'treze', 'quatorze', 'quinze', 'dezesseis', 'dezessete', 'dezoito', 'dezenove']
TENS = ['', 'dez', 'vinte', 'trinta', 'quarenta', 'cinquenta', 'sessenta', 'setenta', 'oitenta', 'noventa']
HUNDREDS = ['', 'cento', 'duzentos', 'trezentos', 'quatrocentos', 'quinhentos', 'seiscentos', 'setecentos', 'oitocentos', 'novecentos']

def int_to_words_pt(n: int) -> str:
    """Converte um número inteiro em palavras em português."""
    if n == 0:
        return 'zero'
    if n == 100:
        return 'cem'
    
    parts = []
    millions = n // 1000000
    rem_mil = n % 1000000
    if millions > 0:
        if millions == 1:
            parts.append('um milhão')
        else:
            parts.append(int_to_words_pt(millions) + ' milhões')

    thousands = rem_mil // 1000
    rem_th = rem_mil % 1000
    if thousands > 0:
        if thousands == 1:
            parts.append('mil')
        else:
            parts.append(int_to_words_pt(thousands) + ' mil')

    if rem_th > 0:
        h = rem_th // 100
        rem_ten = rem_th % 100
        if h > 0:
            if h == 1 and rem_ten == 0:
                parts.append('cem')
            else:
                parts.append(HUNDREDS[h])
        if rem_ten > 0:
            if rem_ten < 10:
                parts.append(UNITS[rem_ten])
            elif rem_ten < 20:
                parts.append(TEENS[rem_ten - 10])
            else:
                t = rem_ten // 10
                u = rem_ten % 10
                parts.append(f"{TENS[t]} e {UNITS[u]}" if u > 0 else TENS[t])

    if len(parts) == 1:
        return parts[0]
    if thousands > 0 and 0 < rem_th < 100:
        return ' e '.join(parts)
    return ' e '.join(parts) if len(parts) == 2 else ', '.join(parts[:-1]) + ' e ' + parts[-1]


def currency_to_words_pt(reais: int, centavos: int = 0) -> str:
    """Converte valor monetário em reais para texto fonético natural."""
    res = []
    if reais > 0:
        r_str = 'um real' if reais == 1 else f"{int_to_words_pt(reais)} reais"
        res.append(r_str)
    if centavos > 0:
        c_str = 'um centavo' if centavos == 1 else f"{int_to_words_pt(centavos)} centavos"
        res.append(c_str)
    return ' e '.join(res) if res else 'zero reais'


# Dicionário de abreviações e gírias de internet para português formal
ABBREVIATIONS = {
    r'\bvc\b': 'você',
    r'\bvcs\b': 'vocês',
    r'\bpq\b': 'porque',
    r'\bp/q\b': 'porque',
    r'\btb\b': 'também',
    r'\btbm\b': 'também',
    r'\bq\b': 'que',
    r'\bblz\b': 'beleza',
    r'\bmsg\b': 'mensagem',
    r'\bmsgs\b': 'mensagens',
    r'\bfds\b': 'fim de semana',
    r'\bvdd\b': 'verdade',
    r'\bcmg\b': 'comigo',
    r'\bctz\b': 'com certeza',
    r'\bplmds\b': 'pelo amor de Deus',
    r'\bpfv\b': 'por favor',
    r'\bpfvr\b': 'por favor',
    r'\bobg\b': 'obrigado',
    r'\bobgd\b': 'obrigado',
    r'\bobgda\b': 'obrigada',
    r'\bp/\b': 'para ',
    r'\bpra\b': 'para',
    r'\bpro\b': 'para o',
    r'\bpros\b': 'para os',
    r'\bpras\b': 'para as',
    r'\bta\b': 'está',
    r'\btá\b': 'está',
    r'\bto\b': 'estou',
    r'\btô\b': 'estou',
    r'\bdr\.\b': 'Doutor',
    r'\bdra\.\b': 'Doutora',
    r'\bsr\.\b': 'Senhor',
    r'\bsra\.\b': 'Senhora',
    r'\betc\.\b': 'e assim por diante',
    r'\betc\b': 'e assim por diante',
}

# Dicionário de restauração de acentos críticos para dicção neural
ACCENT_FIXES = {
    r'\bvoce\b': 'você',
    r'\bvoces\b': 'vocês',
    r'\bja\b': 'já',
    r'\bate\b': 'até',
    r'\btambem\b': 'também',
    r'\bnao\b': 'não',
    r'\bestao\b': 'estão',
    r'\bsao\b': 'são',
    r'\bnumero\b': 'número',
    r'\bnumeros\b': 'números',
    r'\bhistoria\b': 'história',
    r'\bhistorias\b': 'histórias',
    r'\bvideo\b': 'vídeo',
    r'\bvideos\b': 'vídeos',
    r'\baudio\b': 'áudio',
    r'\baudios\b': 'áudios',
    r'\bcamera\b': 'câmera',
    r'\bcameras\b': 'câmeras',
    r'\binteligencia\b': 'inteligência',
    r'\bpublico\b': 'público',
    r'\bconteudo\b': 'conteúdo',
    r'\bexperiencia\b': 'experiência',
    r'\bpagina\b': 'página',
    r'\bpaginas\b': 'páginas',
    r'\bgratis\b': 'grátis',
    r'\bfacil\b': 'fácil',
    r'\bdificil\b': 'difícil',
    r'\botimo\b': 'ótimo',
    r'\botima\b': 'ótima',
    r'\brapido\b': 'rápido',
    r'\brapida\b': 'rápida',
    r'\bincrivel\b': 'incrível',
    r'\bunico\b': 'único',
    r'\bunica\b': 'única',
    r'\bopcao\b': 'opção',
    r'\bopcoes\b': 'opções',
    r'\bproducao\b': 'produção',
    r'\batencao\b': 'atenção',
    r'\bretencao\b': 'retenção',
    r'\bcriacao\b': 'criação',
    r'\bgeracao\b': 'geração',
    r'\bedicao\b': 'edição',
    r'\bgravacao\b': 'gravação',
    r'\bsolucao\b': 'solução',
    r'\bsolucoes\b': 'soluções',
    r'\bconversao\b': 'conversão',
    r'\bpadrao\b': 'padrão',
    r'\bfara\b': 'fará',
    r'\bsera\b': 'será',
    r'\bestara\b': 'estará',
    r'\bapos\b': 'após',
    r'\balem\b': 'além',
    r'\bso\b': 'só',
    r'\bsozinho\b': 'sozinho',
    r'\bsozinha\b': 'sozinha',
    r'\bpolitica\b': 'política',
    r'\bpoliticas\b': 'políticas',
    r'\beconomia\b': 'economia',
    r'\bautomatica\b': 'automática',
    r'\bautomatico\b': 'automático',
    r'\binvisivel\b': 'invisível',
    r'\bpossivel\b': 'possível',
}

# Fonética especializada para síntese auditiva (TTS)
PHONETIC_TTS_REPLACEMENTS = {
    r'\b[Pp][Ii][Xx]\b': 'Pícs',
    r'\bChatGPT\b': 'Chat G P T',
    r'\bchatgpt\b': 'Chat G P T',
    r'\bYouTube\b': 'You Tube',
    r'\byoutube\b': 'You Tube',
    r'\bTikTok\b': 'Tik Tok',
    r'\btiktok\b': 'Tik Tok',
    r'\b[Ww]hats[Aa]pp\b': 'Uátizap',
    r'\b[Ww]pp\b': 'Uátizap',
    r'\b[Zz]ap\b': 'Zap',
    r'\bAI\b': 'inteligência artificial',
    r'\bI\.A\.\b': 'inteligência artificial',
    r'\bIA\b': 'inteligência artificial',
    r'\bDark\b': 'Dark',
    r'\bdark\b': 'Dark',
    r'\bReels\b': 'Ríous',
    r'\breels\b': 'Ríous',
    r'\bShorts\b': 'Xórts',
    r'\bshorts\b': 'Xórts',
}


def normalize_punctuation(text: str) -> str:
    """Corrige pontuação grudada, espaçamentos e pausas respiratórias, preservando números decimais como 9,90."""
    # 1. Espaço após pontuação, mas NUNCA separa números decimais (ex: 9,90 ou 1.500)
    # Entre letra e letra/número:
    text = re.sub(r'([a-zA-ZÀ-ÿ])([,;:\.\!\?])([a-zA-ZÀ-ÿ0-9])', r'\1\2 \3', text)
    # Entre número e letra:
    text = re.sub(r'([0-9])([,;:\.\!\?])([a-zA-ZÀ-ÿ])', r'\1\2 \3', text)
    # Entre número e pontuações que não sejam vírgula ou ponto decimal:
    text = re.sub(r'([0-9])([;:\!\?])([0-9])', r'\1\2 \3', text)

    # 2. Remove espaços antes de pontuações: "palavra ," -> "palavra,"
    text = re.sub(r'\s+([,;:\.\!\?])', r'\1', text)

    # 3. Normaliza exclamações e interrogações repetidas: "!!!" -> "!"
    text = re.sub(r'\!{2,}', '!', text)
    text = re.sub(r'\?{2,}', '?', text)

    # 4. Normaliza reticências excessivas
    text = re.sub(r'\.{4,}', '... ', text)
    text = re.sub(r'\.{3}', '... ', text)

    # 5. Múltiplos espaços e quebras
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def replace_currencies_and_numbers(text: str) -> str:
    """Expande R$ e números para palavras em português."""
    # R$ com centavos: "R$ 9,90", "R$ 1.500,50", "R$9,90", "R$ 9, 90"
    def sub_currency_cents(match):
        val_str = match.group(1).replace('.', '')
        cent_str = match.group(2)
        try:
            reais = int(val_str)
            centavos = int(cent_str)
            return currency_to_words_pt(reais, centavos)
        except Exception:
            return match.group(0)

    text = re.sub(r'R\$\s*(\d+(?:\.\d{3})*)\s*,\s*(\d{2})\b', sub_currency_cents, text, flags=re.IGNORECASE)

    # R$ sem centavos: "R$ 15", "R$ 50", "R$ 1.000"
    def sub_currency_plain(match):
        val_str = match.group(1).replace('.', '')
        try:
            reais = int(val_str)
            return currency_to_words_pt(reais, 0)
        except Exception:
            return match.group(0)

    text = re.sub(r'R\$\s*(\d+(?:\.\d{3})*)\b', sub_currency_plain, text, flags=re.IGNORECASE)

    # Porcentagens: "100%", "50%"
    def sub_percent(match):
        val = int(match.group(1))
        return f"{int_to_words_pt(val)} por cento"

    text = re.sub(r'\b(\d+)%', sub_percent, text)

    # Medidas comuns
    text = re.sub(r'\b(\d+)\s*kg\b', lambda m: f"{int_to_words_pt(int(m.group(1)))} quilos", text, flags=re.IGNORECASE)
    text = re.sub(r'\b(\d+)\s*km\b', lambda m: f"{int_to_words_pt(int(m.group(1)))} quilômetros", text, flags=re.IGNORECASE)
    text = re.sub(r'\b(\d+)\s*min\b', lambda m: f"{int_to_words_pt(int(m.group(1)))} minutos", text, flags=re.IGNORECASE)
    text = re.sub(r'\b(\d+)\s*seg\b', lambda m: f"{int_to_words_pt(int(m.group(1)))} segundos", text, flags=re.IGNORECASE)

    return text


def capitalize_sentences(text: str) -> str:
    """Garante que o início de frases comece com letra maiúscula."""
    sentences = re.split(r'([\.\!\?]\s+)', text)
    result = []
    for s in sentences:
        if s and not re.match(r'[\.\!\?]\s+', s):
            s = s[0].upper() + s[1:] if len(s) > 1 else s.upper()
        result.append(s)
    return ''.join(result)


def enhance_text_for_display(text: str) -> dict:
    """
    Melhora gramática, acentuação e pontuação para exibição no editor.
    O usuário pode ver o texto corrigido na tela.
    """
    if not text or not text.strip():
        return {"original": text, "enhanced": text, "changes": 0}

    original = text.strip()
    result = original

    # 1. Normalização de pontuações
    result = normalize_punctuation(result)

    # 2. Expansão de abreviações de internet
    for pattern, rep in ABBREVIATIONS.items():
        result = re.sub(pattern, rep, result, flags=re.IGNORECASE)

    # 3. Correção de acentos críticos
    for pattern, rep in ACCENT_FIXES.items():
        result = re.sub(pattern, rep, result, flags=re.IGNORECASE)

    # 4. Formata "ChatGPT", "WhatsApp", "YouTube"
    result = re.sub(r'\bchatgpt\b', 'ChatGPT', result, flags=re.IGNORECASE)
    result = re.sub(r'\byoutube\b', 'YouTube', result, flags=re.IGNORECASE)
    result = re.sub(r'\bwhatsapp\b', 'WhatsApp', result, flags=re.IGNORECASE)
    result = re.sub(r'\bpix\b', 'PIX', result, flags=re.IGNORECASE)

    # 5. Capitalização de sentenças
    result = capitalize_sentences(result)

    # 6. Pontuação final se estiver ausente
    if result and not result.endswith(('.', '!', '?', '...')):
        result += '.'

    changes = 1 if result != original else 0

    return {
        "original": original,
        "enhanced": result,
        "changes": changes
    }


def normalize_for_tts(text: str) -> str:
    """
    Normalização avançada aplicada internamente no motor neural de voz.
    Converte moedas, siglas e fonética para que a IA fale perfeitamente sem tropeçar.
    """
    if not text or not text.strip():
        return ""

    # 1. Aplica melhorias ortográficas de base
    display_info = enhance_text_for_display(text)
    norm = display_info["enhanced"]

    # 2. Converte moedas e números para palavras
    norm = replace_currencies_and_numbers(norm)

    # 3. Ajustes fonéticos específicos para o leitor neural
    for pattern, phonetic in PHONETIC_TTS_REPLACEMENTS.items():
        norm = re.sub(pattern, phonetic, norm)

    # 4. Garante pontuação final
    norm = norm.strip()
    if norm and not norm.endswith(('.', '!', '?', '...')):
        norm += '.'

    return norm
