import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { GoogleGenAI } from "@google/genai";

export const GEMINI_OFFICIAL_VOICES = [
  { name: "Kore", gender: "Feminina", timbre: "Firme & Comercial", defaultStyle: "Voz firme, natural, clara e persuasiva em português brasileiro." },
  { name: "Charon", gender: "Masculina", timbre: "Grave & Narrativo", defaultStyle: "Voz grave, informativa, segura e envolvente em português brasileiro." },
  { name: "Puck", gender: "Masculina", timbre: "Jovem & Dinâmico", defaultStyle: "Voz animada, ágil e expressiva para conteúdos dinâmicos em português brasileiro." },
  { name: "Fenrir", gender: "Masculina", timbre: "Expressivo & Quente", defaultStyle: "Voz vibrante, intensa e empolgante em português brasileiro." },
  { name: "Zephyr", gender: "Feminina", timbre: "Sereno & Claro", defaultStyle: "Voz brilhante, leve e articulada em português brasileiro." },
  { name: "Aoede", gender: "Feminina", timbre: "Suave & Acolhedor", defaultStyle: "Voz fluida, leve e natural para conversas e vídeos em português brasileiro." },
  { name: "Leda", gender: "Feminina", timbre: "Jovem & Dinâmico", defaultStyle: "Voz jovem, doce e espontânea em português brasileiro." },
  { name: "Orus", gender: "Masculina", timbre: "Firme & Comercial", defaultStyle: "Voz firme, direta e autoritativa para locuções comerciais em português brasileiro." },
  { name: "Callirrhoe", gender: "Feminina", timbre: "Suave & Acolhedor", defaultStyle: "Voz tranquila, amigável e descontraída em português brasileiro." },
  { name: "Autonoe", gender: "Feminina", timbre: "Sereno & Claro", defaultStyle: "Voz luminosa, otimista e nítida em português brasileiro." },
  { name: "Enceladus", gender: "Masculina", timbre: "Suave & Acolhedor", defaultStyle: "Voz suave, soprada e intimista para narrativas calmas em português brasileiro." },
  { name: "Iapetus", gender: "Masculina", timbre: "Sereno & Claro", defaultStyle: "Voz limpa, clara e equilibrada em português brasileiro." },
  { name: "Umbriel", gender: "Masculina", timbre: "Suave & Acolhedor", defaultStyle: "Voz relaxada, calorosa e acessível em português brasileiro." },
  { name: "Algieba", gender: "Masculina", timbre: "Suave & Acolhedor", defaultStyle: "Voz macia, polida e agradável em português brasileiro." },
  { name: "Despina", gender: "Feminina", timbre: "Suave & Acolhedor", defaultStyle: "Voz suave, elegante e fluida em português brasileiro." },
  { name: "Erinome", gender: "Feminina", timbre: "Sereno & Claro", defaultStyle: "Voz cristalina, didática e bem articulada em português brasileiro." },
  { name: "Algenib", gender: "Masculina", timbre: "Grave & Narrativo", defaultStyle: "Voz texturizada, grave e marcante para documentários e histórias em português brasileiro." },
  { name: "Rasalgethi", gender: "Masculina", timbre: "Sereno & Claro", defaultStyle: "Voz informativa, jornalística e objetiva em português brasileiro." },
  { name: "Laomedeia", gender: "Feminina", timbre: "Jovem & Dinâmico", defaultStyle: "Voz alegre, viva e carismática em português brasileiro." },
  { name: "Achernar", gender: "Feminina", timbre: "Suave & Acolhedor", defaultStyle: "Voz gentil, macia e acolhedora em português brasileiro." },
  { name: "Alnilam", gender: "Masculina", timbre: "Firme & Comercial", defaultStyle: "Voz forte, decidida e confiável em português brasileiro." },
  { name: "Schedar", gender: "Masculina", timbre: "Sereno & Claro", defaultStyle: "Voz equilibrada, realista e sem exageros em português brasileiro." },
  { name: "Gacrux", gender: "Feminina", timbre: "Grave & Narrativo", defaultStyle: "Voz madura, experiente e envolvente para narrações em português brasileiro." },
  { name: "Pulcherrima", gender: "Feminina", timbre: "Expressivo & Quente", defaultStyle: "Voz emotiva, expressiva e cativante em português brasileiro." },
  { name: "Achird", gender: "Masculina", timbre: "Suave & Acolhedor", defaultStyle: "Voz amigável, próxima e simpática em português brasileiro." },
  { name: "Zubenelgenubi", gender: "Masculina", timbre: "Jovem & Dinâmico", defaultStyle: "Voz casual, cotidiana e espontânea em português brasileiro." },
  { name: "Vindemiatrix", gender: "Feminina", timbre: "Suave & Acolhedor", defaultStyle: "Voz meiga, delicada e calma em português brasileiro." },
  { name: "Sadachbia", gender: "Feminina", timbre: "Expressivo & Quente", defaultStyle: "Voz vivaz, enérgica e expressiva em português brasileiro." },
  { name: "Sadaltager", gender: "Masculina", timbre: "Grave & Narrativo", defaultStyle: "Voz sábia, explicativa e segura em português brasileiro." },
  { name: "Sulafat", gender: "Feminina", timbre: "Expressivo & Quente", defaultStyle: "Voz calorosa, envolvente e humana em português brasileiro." }
];

const OFFICIAL_VOICE_NAMES = new Set(GEMINI_OFFICIAL_VOICES.map((v) => v.name.toLowerCase()));

export function resolveGeminiVoiceName(voiceKey) {
  if (!voiceKey) return "Kore";
  const cleaned = String(voiceKey).trim();
  const direct = GEMINI_OFFICIAL_VOICES.find((v) => v.name.toLowerCase() === cleaned.toLowerCase());
  if (direct) return direct.name;

  // Mapeamento de compatibilidade com vozes legadas
  const legacyMap = {
    el_su: "Kore",
    su: "Kore",
    custom_su: "Kore",
    sarah: "Aoede",
    eduarda: "Leda",
    duda: "Sadachbia",
    dii: "Vindemiatrix",
    faber: "Orus",
    thalita: "Pulcherrima",
    el_bella: "Despina",
    el_alice: "Zephyr",
    el_jessica: "Laomedeia",
    el_laura: "Achernar",
    el_rachel: "Gacrux",
    jeff: "Puck",
    cadu: "Fenrir",
    miro: "Charon",
    edresson: "Schedar",
    el_adam: "Charon",
    el_brian: "Alnilam",
    el_daniel: "Rasalgethi",
    el_liam: "Puck",
    el_george: "Sadaltager",
    el_charlie: "Zubenelgenubi",
    el_chris: "Iapetus"
  };

  if (legacyMap[cleaned.toLowerCase()]) {
    return legacyMap[cleaned.toLowerCase()];
  }
  return "Kore";
}

function escapeRegExp(str) {
  return String(str).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function parseDialogueBlocks({ text, dialogue, speakers, defaultStyle }) {
  const speakerList = Array.isArray(speakers) && speakers.length >= 2
    ? speakers.slice(0, 2).map((sp, idx) => ({
        speaker: String(sp.speaker || `Locutor ${idx + 1}`).trim() || `Locutor ${idx + 1}`,
        voice: resolveGeminiVoiceName(sp.voice || (idx === 0 ? "Kore" : "Charon")),
        style: String(sp.style || defaultStyle || "Voz natural, clara e expressiva").trim(),
        language: sp.language || "pt-BR"
      }))
    : [
        { speaker: "Locutor 1", voice: "Kore", style: defaultStyle || "Voz natural, clara e expressiva", language: "pt-BR" },
        { speaker: "Locutor 2", voice: "Charon", style: defaultStyle || "Voz natural, clara e expressiva", language: "pt-BR" }
      ];

  const styleBySpeaker = new Map(speakerList.map((s) => [s.speaker.toLowerCase(), s.style]));

  if (Array.isArray(dialogue) && dialogue.length > 0) {
    const cleanTurns = dialogue
      .map((item, idx) => {
        const spName = String(item.speaker || speakerList[idx % 2].speaker).trim();
        const turnText = String(item.text || "").trim();
        const turnStyle = String(
          item.style || styleBySpeaker.get(spName.toLowerCase()) || defaultStyle || "Voz natural, clara e expressiva"
        ).trim();
        if (!turnText) return null;
        return {
          type: "text",
          text: turnText,
          annotations: [
            {
              type: "speech_metadata",
              speaker: spName,
              style: turnStyle
            }
          ]
        };
      })
      .filter(Boolean);

    if (cleanTurns.length > 0) {
      return { inputBlocks: cleanTurns, speakerConfigs: speakerList };
    }
  }

  // Fallback: parseia linhas do texto no formato "Nome: fala" ou alternando entre os 2 locutores
  const lines = String(text || "")
    .replace(/\r\n/g, "\n")
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean);

  const sp1 = speakerList[0];
  const sp2 = speakerList[1];
  const p1 = new RegExp(`^${escapeRegExp(sp1.speaker)}\\s*:\\s*(.+)$`, "i");
  const p2 = new RegExp(`^${escapeRegExp(sp2.speaker)}\\s*:\\s*(.+)$`, "i");
  const genericPrefix = /^([^:\n]{1,30})\s*:\s*(.+)$/;

  const blocks = [];
  let turnIndex = 0;

  for (const line of lines) {
    let chosenSpeaker = null;
    let lineText = line;

    const m1 = line.match(p1);
    const m2 = line.match(p2);
    if (m1) {
      chosenSpeaker = sp1;
      lineText = m1[1].trim();
    } else if (m2) {
      chosenSpeaker = sp2;
      lineText = m2[1].trim();
    } else {
      const gen = line.match(genericPrefix);
      if (gen && !/^https?$/i.test(gen[1])) {
        const prefixLower = gen[1].trim().toLowerCase();
        if (prefixLower === sp2.speaker.toLowerCase() || prefixLower === "2" || prefixLower === "b") {
          chosenSpeaker = sp2;
        } else {
          chosenSpeaker = turnIndex % 2 === 0 ? sp1 : sp2;
        }
        lineText = gen[2].trim();
      } else {
        chosenSpeaker = turnIndex % 2 === 0 ? sp1 : sp2;
      }
    }

    if (lineText) {
      blocks.push({
        type: "text",
        text: lineText,
        annotations: [
          {
            type: "speech_metadata",
            speaker: chosenSpeaker.speaker,
            style: chosenSpeaker.style || "Voz natural, clara e expressiva"
          }
        ]
      });
      turnIndex += 1;
    }
  }

  if (blocks.length === 0) {
    blocks.push({
      type: "text",
      text: String(text || "").trim(),
      annotations: [
        {
          type: "speech_metadata",
          speaker: sp1.speaker,
          style: sp1.style
        }
      ]
    });
  }

  return { inputBlocks: blocks, speakerConfigs: speakerList };
}

export async function synthesizeWithGemini({
  text = "",
  voice = "Kore",
  style = "Voz natural, clara e expressiva",
  mode = "single",
  model = null,
  language = "pt-BR",
  dialogue = null,
  speakers = null,
  outputWavPath
}) {
  const apiKey = (process.env.GEMINI_API_KEY || "").trim();
  if (!apiKey) {
    throw new Error("GEMINI_API_KEY não configurada no ambiente do servidor.");
  }
  if (!outputWavPath) {
    throw new Error("outputWavPath é obrigatório.");
  }

  const ai = new GoogleGenAI({ apiKey });
  const normalizedMode = String(mode || "single").toLowerCase();

  let selectedModel = model ? String(model).trim() : null;
  if (!selectedModel) {
    selectedModel =
      normalizedMode === "dialogue" || normalizedMode === "expressive"
        ? "gemini-3.8-flash-tts"
        : "gemini-3.8-flash-lite-tts";
  }

  let requestPayload;

  if (normalizedMode === "dialogue") {
    selectedModel = "gemini-3.8-flash-tts";
    const { inputBlocks, speakerConfigs } = parseDialogueBlocks({
      text,
      dialogue,
      speakers,
      defaultStyle: style
    });

    requestPayload = {
      model: selectedModel,
      input: inputBlocks,
      response_format: { type: "audio" },
      generation_config: {
        speech_config: {
          speakers: speakerConfigs.map((sp) => ({
            speaker: sp.speaker,
            voice: sp.voice
          }))
        }
      }
    };
  } else {
    const resolvedVoice = resolveGeminiVoiceName(voice);
    const estiloVocal = String(style || "Voz natural, clara e expressiva").trim();

    requestPayload = {
      model: selectedModel,
      input: [
        {
          type: "text",
          text: String(text || "").trim(),
          annotations: [
            {
              type: "speech_metadata",
              style: estiloVocal
            }
          ]
        }
      ],
      response_format: { type: "audio" },
      generation_config: {
        speech_config: [
          {
            language: language || "pt-BR",
            voice: resolvedVoice
          }
        ]
      }
    };
  }

  const interaction = await ai.interactions.create(requestPayload);
  const audioBase64 = interaction.output_audio?.data;
  if (!audioBase64) {
    throw new Error("A API Gemini TTS não retornou output_audio.data.");
  }

  const audioBuffer = Buffer.from(audioBase64, "base64");
  fs.mkdirSync(path.dirname(path.resolve(outputWavPath)), { recursive: true });
  fs.writeFileSync(outputWavPath, audioBuffer);

  return {
    success: true,
    model: selectedModel,
    mode: normalizedMode,
    mime_type: interaction.output_audio?.mime_type || "audio/wav",
    sample_rate: interaction.output_audio?.sample_rate || 24000,
    channels: interaction.output_audio?.channels || 1,
    bytes: audioBuffer.length,
    output_wav_path: outputWavPath
  };
}

export function isOfficialGeminiVoice(voiceKey) {
  return OFFICIAL_VOICE_NAMES.has(String(voiceKey || "").trim().toLowerCase());
}

async function readCliPayload() {
  const args = process.argv.slice(2);
  const inputFileIdx = args.indexOf("--input-file");
  if (inputFileIdx !== -1 && args[inputFileIdx + 1]) {
    const raw = fs.readFileSync(args[inputFileIdx + 1], "utf8");
    return JSON.parse(raw);
  }
  const chunks = [];
  for await (const chunk of process.stdin) {
    chunks.push(chunk);
  }
  const raw = Buffer.concat(chunks).toString("utf8").trim();
  if (!raw) {
    throw new Error("Nenhum payload JSON recebido via --input-file ou stdin.");
  }
  return JSON.parse(raw);
}

const isMainModule =
  process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href;

if (isMainModule) {
  try {
    const payload = await readCliPayload();
    const result = await synthesizeWithGemini(payload);
    process.stdout.write(JSON.stringify(result));
  } catch (err) {
    const message = err?.message || String(err);
    process.stderr.write(JSON.stringify({ success: false, error: message }) + "\n");
    process.exit(1);
  }
}
