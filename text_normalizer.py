"""
VOXSTUDIO / CLONAVOZ - Módulo de Normalização Gramatical, Fonética e Análise de Dicção PT-BR
Garante dicção perfeita, pontuação respiratória, detecção de erros coloquiais e termo de isenção.
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


# Dicionário de correções coloquiais, internet e faladas
COLLOQUIAL_RULES = [
    (r'\b[Oo]nti\b', 'Ontem', 'onti', 'ontem', 'Gíria oral que causa pronúncia cortada ou estranha.'),
    (r'\bnum\s+(pude|posso|sei|quero|vou|vai|deu|tinha|é|consigo|faz)\b', r'não \1', 'num', 'não', 'Linguagem coloquial falada.'),
    (r',\s*mais\s+(eu|ele|ela|nós|eles|elas|não|num|ninguém|alguém)\b', r', mas \1', 'mais', 'mas', 'Uso indevido de "mais" (adição) em vez de "mas" (oposição).'),
    (r'\bmais\s+(eu|ele|ela|nós|eles|elas)\b', r'mas \1', 'mais', 'mas', 'Uso indevido de "mais" em vez de "mas".'),
    (r'\bta\b', 'está', 'ta', 'está', 'Abreviação coloquial do verbo estar.'),
    (r'\btá\b', 'está', 'tá', 'está', 'Forma coloquial do verbo estar.'),
    (r'\bto\b', 'estou', 'to', 'estou', 'Abreviação coloquial do verbo estar.'),
    (r'\btô\b', 'estou', 'tô', 'estou', 'Forma coloquial do verbo estar.'),
    (r'\btava\b', 'estava', 'tava', 'estava', 'Forma coloquial do verbo estar no pretérito.'),
    (r'\btavam\b', 'estavam', 'tavam', 'estavam', 'Forma coloquial do verbo estar no plural.'),
    (r'\btamo\b', 'estamos', 'tamo', 'estamos', 'Forma coloquial de estamos.'),
    (r'\btamos\b', 'estamos', 'tamos', 'estamos', 'Forma coloquial de estamos.'),
    (r'\bpra\b', 'para', 'pra', 'para', 'Contração coloquial de para.'),
    (r'\bpro\b', 'para o', 'pro', 'para o', 'Contração coloquial de para o.'),
    (r'\bpros\b', 'para os', 'pros', 'para os', 'Contração coloquial de para os.'),
    (r'\bpras\b', 'para as', 'pras', 'para as', 'Contração coloquial de para as.'),
    (r'\bvc\b', 'você', 'vc', 'você', 'Abreviação de internet.'),
    (r'\bvcs\b', 'vocês', 'vcs', 'vocês', 'Abreviação de internet.'),
    (r'\bpq\b', 'porque', 'pq', 'porque', 'Abreviação de internet.'),
    (r'\bp/q\b', 'porque', 'p/q', 'porque', 'Abreviação de internet.'),
    (r'\btb\b', 'também', 'tb', 'também', 'Abreviação de internet.'),
    (r'\btbm\b', 'também', 'tbm', 'também', 'Abreviação de internet.'),
    (r'\bq\b', 'que', 'q', 'que', 'Abreviação de internet.'),
    (r'\bblz\b', 'beleza', 'blz', 'beleza', 'Gíria de internet.'),
    (r'\bmsg\b', 'mensagem', 'msg', 'mensagem', 'Abreviação de mensagem.'),
    (r'\bmsgs\b', 'mensagens', 'msgs', 'mensagens', 'Abreviação de mensagens.'),
    (r'\bfds\b', 'fim de semana', 'fds', 'fim de semana', 'Abreviação de fim de semana.'),
    (r'\bvdd\b', 'verdade', 'vdd', 'verdade', 'Abreviação de verdade.'),
    (r'\bcmg\b', 'comigo', 'cmg', 'comigo', 'Abreviação de comigo.'),
    (r'\bctz\b', 'com certeza', 'ctz', 'com certeza', 'Abreviação de com certeza.'),
    (r'\bpfv\b', 'por favor', 'pfv', 'por favor', 'Abreviação de por favor.'),
    (r'\bpfvr\b', 'por favor', 'pfvr', 'por favor', 'Abreviação de por favor.'),
    (r'\bobg\b', 'obrigado', 'obg', 'obrigado', 'Abreviação de obrigado.'),
    (r'\bobgd\b', 'obrigado', 'obgd', 'obrigado', 'Abreviação de obrigado.'),
    (r'\bp/\b', 'para ', 'p/', 'para', 'Abreviação de para.'),
]

# Verbos sem "r" final no infinitivo precedidos de auxiliares (ex: tendo que paga -> pagar)
INFINITIVE_VERB_ROOTS = [
    'paga', 'faze', 'anda', 'corre', 'come', 'compra', 'vende', 'olha', 'ajuda', 'escuta',
    'fala', 'resolve', 'escreve', 'bebe', 'mexe', 'cria', 'grava', 'aprende', 'descobre'
]

# Dicionário de palavras frequentes sem acento que afetam tonicidade e dicção
ACCENT_RULES = [
    (r'\bla\b', 'lá', 'la', 'lá', 'Ausência de acento altera a sílaba tônica.'),
    (r'\bja\b', 'já', 'ja', 'já', 'Ausência de acento altera a pronúncia.'),
    (r'\bmes\b', 'mês', 'mes', 'mês', 'Ausência de acento fecha o som incorretamente.'),
    (r'\bate\b', 'até', 'ate', 'até', 'Sem acento soa como o verbo atar (ate).'),
    (r'\bso\b', 'só', 'so', 'só', 'Sem acento fecha o som em "so".'),
    (r'\bvoce\b', 'você', 'voce', 'você', 'Sem acento oxítono.'),
    (r'\bvoces\b', 'vocês', 'voces', 'vocês', 'Sem acento oxítono.'),
    (r'\btambem\b', 'também', 'tambem', 'também', 'Sem acento oxítono nasal.'),
    (r'\bnao\b', 'não', 'nao', 'não', 'Sem til nasal.'),
    (r'\bestao\b', 'estão', 'estao', 'estão', 'Sem til nasal.'),
    (r'\bsao\b', 'são', 'sao', 'são', 'Sem til nasal.'),
    (r'\bvarios\b', 'vários', 'varios', 'vários', 'Sem acento proparoxítono/paroxítono.'),
    (r'\bvarias\b', 'várias', 'varias', 'várias', 'Sem acento proparoxítono/paroxítono.'),
    (r'\bautomovel\b', 'automóvel', 'automovel', 'automóvel', 'Sem acento paroxítono em l.'),
    (r'\bautomoveis\b', 'automóveis', 'automoveis', 'automóveis', 'Sem acento paroxítono.'),
    (r'\bonibus\b', 'ônibus', 'onibus', 'ônibus', 'Proparoxítona sem acento circunflexo.'),
    (r'\bnumero\b', 'número', 'numero', 'número', 'Sem acento proparoxítono.'),
    (r'\bnumeros\b', 'números', 'numeros', 'números', 'Sem acento proparoxítono.'),
    (r'\bhistoria\b', 'história', 'historia', 'história', 'Sem acento paroxítono terminado em ditongo.'),
    (r'\bhistorias\b', 'histórias', 'historias', 'histórias', 'Sem acento paroxítono.'),
    (r'\bvideo\b', 'vídeo', 'video', 'vídeo', 'Sem acento paroxítono em ditongo.'),
    (r'\bvideos\b', 'vídeos', 'videos', 'vídeos', 'Sem acento paroxítono.'),
    (r'\baudio\b', 'áudio', 'audio', 'áudio', 'Sem acento paroxítono em ditongo.'),
    (r'\baudios\b', 'áudios', 'audios', 'áudios', 'Sem acento paroxítono.'),
    (r'\bcamera\b', 'câmera', 'camera', 'câmera', 'Proparoxítona sem acento.'),
    (r'\bcameras\b', 'câmeras', 'cameras', 'câmeras', 'Proparoxítona sem acento.'),
    (r'\binteligencia\b', 'inteligência', 'inteligencia', 'inteligência', 'Sem acento circunflexo em ditongo.'),
    (r'\bpublico\b', 'público', 'publico', 'público', 'Sem acento soa como verbo publicar (publico).'),
    (r'\bconteudo\b', 'conteúdo', 'conteudo', 'conteúdo', 'Sem acento agudo no hiato em u.'),
    (r'\bexperiencia\b', 'experiência', 'experiencia', 'experiência', 'Sem acento circunflexo em ditongo.'),
    (r'\bpagina\b', 'página', 'pagina', 'página', 'Proparoxítona sem acento.'),
    (r'\bpaginas\b', 'páginas', 'paginas', 'páginas', 'Proparoxítona sem acento.'),
    (r'\bgratis\b', 'grátis', 'gratis', 'grátis', 'Paroxítona terminada em is sem acento.'),
    (r'\bfacil\b', 'fácil', 'facil', 'fácil', 'Paroxítona em l sem acento.'),
    (r'\bdificil\b', 'difícil', 'dificil', 'difícil', 'Paroxítona em l sem acento.'),
    (r'\botimo\b', 'ótimo', 'otimo', 'ótimo', 'Proparoxítona sem acento.'),
    (r'\botima\b', 'ótima', 'otima', 'ótima', 'Proparoxítona sem acento.'),
    (r'\brapido\b', 'rápido', 'rapido', 'rápido', 'Proparoxítona sem acento.'),
    (r'\brapida\b', 'rápida', 'rapida', 'rápida', 'Proparoxítona sem acento.'),
    (r'\bincrivel\b', 'incrível', 'incrivel', 'incrível', 'Paroxítona em l sem acento.'),
    (r'\bunico\b', 'único', 'unico', 'único', 'Proparoxítona sem acento.'),
    (r'\bunica\b', 'única', 'unica', 'única', 'Proparoxítona sem acento.'),
    (r'\bopcao\b', 'opção', 'opcao', 'opção', 'Sem til nem cedilha.'),
    (r'\bopcoes\b', 'opções', 'opcoes', 'opções', 'Sem til nem cedilha.'),
    (r'\bproducao\b', 'produção', 'producao', 'produção', 'Sem til nem cedilha.'),
    (r'\batencao\b', 'atenção', 'atencao', 'atenção', 'Sem til nem cedilha.'),
    (r'\bretencao\b', 'retenção', 'retencao', 'retenção', 'Sem til nem cedilha.'),
    (r'\bcriacao\b', 'criação', 'criacao', 'criação', 'Sem til nem cedilha.'),
    (r'\bedicao\b', 'edição', 'edicao', 'edição', 'Sem til nem cedilha.'),
    (r'\bgravacao\b', 'gravação', 'gravacao', 'gravação', 'Sem til nem cedilha.'),
    (r'\bsolucao\b', 'solução', 'solucao', 'solução', 'Sem til nem cedilha.'),
    (r'\bsolucoes\b', 'soluções', 'solucoes', 'soluções', 'Sem til nem cedilha.'),
    (r'\bconversao\b', 'conversão', 'conversao', 'conversão', 'Sem til nasal.'),
    (r'\bpadrao\b', 'padrão', 'padrao', 'padrão', 'Sem til nasal.'),
    (r'\bfara\b', 'fará', 'fara', 'fará', 'Sem acento oxítono.'),
    (r'\bsera\b', 'será', 'sera', 'será', 'Sem acento oxítono.'),
    (r'\bestara\b', 'estará', 'estara', 'estará', 'Sem acento oxítono.'),
    (r'\bpolitica\b', 'política', 'politica', 'política', 'Proparoxítona sem acento.'),
    (r'\bpoliticas\b', 'políticas', 'politicas', 'políticas', 'Proparoxítona sem acento.'),
    (r'\bpossivel\b', 'possível', 'possivel', 'possível', 'Paroxítona em l sem acento.'),
]

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
    """Corrige pontuação grudada, espaçamentos e pausas respiratórias, preservando decimais."""
    text = re.sub(r'([a-zA-ZÀ-ÿ])([,;:\.\!\?])([a-zA-ZÀ-ÿ0-9])', r'\1\2 \3', text)
    text = re.sub(r'([0-9])([,;:\.\!\?])([a-zA-ZÀ-ÿ])', r'\1\2 \3', text)
    text = re.sub(r'([0-9])([;:\!\?])([0-9])', r'\1\2 \3', text)
    text = re.sub(r'\s+([,;:\.\!\?])', r'\1', text)
    text = re.sub(r'\!{2,}', '!', text)
    text = re.sub(r'\?{2,}', '?', text)
    text = re.sub(r'\.{4,}', '... ', text)
    text = re.sub(r'\.{3}', '... ', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def replace_currencies_and_numbers(text: str) -> str:
    """Expande R$ e números para palavras em português."""
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

    def sub_currency_plain(match):
        val_str = match.group(1).replace('.', '')
        try:
            reais = int(val_str)
            return currency_to_words_pt(reais, 0)
        except Exception:
            return match.group(0)

    text = re.sub(r'R\$\s*(\d+(?:\.\d{3})*)\b', sub_currency_plain, text, flags=re.IGNORECASE)
    text = re.sub(r'\b(\d+)%', lambda m: f"{int_to_words_pt(int(m.group(1)))} por cento", text)
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


def analyze_text_quality(text: str) -> dict:
    """
    Analisa profundamente o texto para identificar gírias, erros gramaticais e falta de acentos.
    Gera lista de problemas detectados, texto corrigido e justificativa para retirada de responsabilidade.
    """
    if not text or not text.strip():
        return {
            "has_issues": False,
            "issues_count": 0,
            "issues_details": [],
            "original_text": text,
            "suggested_text": text,
            "risk_explanation": "",
            "disclaimer": ""
        }

    original = text.strip()
    working = original
    issues = []

    # 1. Checa pontuação
    norm_p = normalize_punctuation(working)
    if norm_p != working:
        issues.append({
            "original": "Espaçamento/Pontuação",
            "suggestion": "Pontuação natural",
            "type": "pausa_respiratoria",
            "reason": "Frases sem pontuação correta fazem a voz neural acelerar e falar sem respirar."
        })
        working = norm_p

    # 2. Checa regras coloquiais
    for pattern, rep, label_orig, label_rep, explanation in COLLOQUIAL_RULES:
        if re.search(pattern, working, flags=re.IGNORECASE):
            issues.append({
                "original": label_orig,
                "suggestion": label_rep,
                "type": "coloquial_giria",
                "reason": explanation
            })
            working = re.sub(pattern, rep, working, flags=re.IGNORECASE)

    # 3. Checa verbos no infinitivo faltando "r" (ex: tendo que paga -> pagar)
    inf_pattern = r'\b(tendo\s+que|tem\s+que|ter\s+que|vai|ia|para|sem|ao)\s+(' + '|'.join(INFINITIVE_VERB_ROOTS) + r')\b'
    matches_inf = re.findall(inf_pattern, working, flags=re.IGNORECASE)
    for aux, v_root in matches_inf:
        v_corr = "fazer" if v_root.lower() == "faze" else (v_root + "r")
        issues.append({
            "original": f"{aux} {v_root}",
            "suggestion": f"{aux} {v_corr}",
            "type": "verbo_infinitivo",
            "reason": f"O verbo '{v_root}' sem 'r' soa truncado ou com erro de concordância na voz neural."
        })
    working = re.sub(inf_pattern, lambda m: m.group(1) + ' ' + ('fazer' if m.group(2).lower() == 'faze' else m.group(2) + 'r'), working, flags=re.IGNORECASE)

    # 4. Checa regras de acentuação
    for pattern, rep, label_orig, label_rep, explanation in ACCENT_RULES:
        if re.search(pattern, working, flags=re.IGNORECASE):
            issues.append({
                "original": label_orig,
                "suggestion": label_rep,
                "type": "falta_acento",
                "reason": explanation
            })
            working = re.sub(pattern, rep, working, flags=re.IGNORECASE)

    # 5. Formata marcas e nomes
    working = re.sub(r'\bchatgpt\b', 'ChatGPT', working, flags=re.IGNORECASE)
    working = re.sub(r'\byoutube\b', 'YouTube', working, flags=re.IGNORECASE)
    working = re.sub(r'\bwhatsapp\b', 'WhatsApp', working, flags=re.IGNORECASE)
    working = re.sub(r'\bpix\b', 'PIX', working, flags=re.IGNORECASE)

    # 6. Capitalização
    working = capitalize_sentences(working)

    # 7. Pontuação final
    if working and not working.endswith(('.', '!', '?', '...')):
        working += '.'

    has_issues = len(issues) > 0 or working != original

    risk_explanation = (
        "A inteligência artificial lê exatamente os fonemas da grafia enviada. "
        "Palavras com gírias orais (como 'onti', 'num', 'ta'), falta de 'r' em verbos (como 'paga') "
        "ou palavras sem acento (como 'la', 'mes', 'onibus') fazem a voz neural mudar a sílaba tônica, "
        "cortar o som ou soar robotizada e confusa."
    )

    disclaimer = (
        "Termo de Isenção de Responsabilidade Fonética: "
        "O usuário declara ciência de que o motor neural de voz sintetiza o texto estritamente de acordo "
        "com a grafia fornecida. Ao optar por manter expressões coloquiais, gírias ou erros ortográficos "
        "sem acatar as correções recomendadas, o usuário isenta o Clonavoz de qualquer responsabilidade "
        "sobre desvios de pronúncia, cortes fonéticos ou sonoridade não natural no áudio gerado."
    )

    return {
        "has_issues": has_issues,
        "issues_count": len(issues),
        "issues_details": issues[:12], # Mostra os principais para não poluir
        "original_text": original,
        "suggested_text": working,
        "risk_explanation": risk_explanation,
        "disclaimer": disclaimer
    }


def enhance_text_for_display(text: str) -> dict:
    """Wrapper para exibição direta no editor."""
    analysis = analyze_text_quality(text)
    return {
        "original": analysis["original_text"],
        "enhanced": analysis["suggested_text"],
        "changes": analysis["issues_count"],
        "analysis": analysis
    }


def normalize_for_tts(text: str) -> str:
    """
    Normalização avançada aplicada internamente no motor neural de voz.
    Converte moedas, siglas e fonética para que a IA fale perfeitamente sem tropeçar.
    """
    if not text or not text.strip():
        return ""

    analysis = analyze_text_quality(text)
    norm = analysis["suggested_text"]

    # Converte moedas e números para palavras
    norm = replace_currencies_and_numbers(norm)

    # Ajustes fonéticos específicos para o leitor neural
    for pattern, phonetic in PHONETIC_TTS_REPLACEMENTS.items():
        norm = re.sub(pattern, phonetic, norm)

    norm = norm.strip()
    if norm and not norm.endswith(('.', '!', '?', '...')):
        norm += '.'

    return norm
