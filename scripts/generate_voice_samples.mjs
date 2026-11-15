import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { GoogleGenAI } from "@google/genai";
import { GEMINI_OFFICIAL_VOICES } from "../gemini_tts_service.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, "..");
const SAMPLES_DIR = path.join(ROOT_DIR, "public", "voice-samples");

function loadDotEnvFallback() {
  if (process.env.GEMINI_API_KEY) return;
  const envPath = path.join(ROOT_DIR, ".env");
  if (!fs.existsSync(envPath)) return;
  const lines = fs.readFileSync(envPath, "utf8").split(/\r?\n/);
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eqIdx = trimmed.indexOf("=");
    if (eqIdx === -1) continue;
    const key = trimmed.slice(0, eqIdx).trim();
    let val = trimmed.slice(eqIdx + 1).trim();
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    if (key && !(key in process.env)) {
      process.env[key] = val;
    }
  }
}

async function main() {
  loadDotEnvFallback();

  const apiKey = (process.env.GEMINI_API_KEY || "").trim();
  if (!apiKey) {
    console.error("[ERRO] GEMINI_API_KEY não configurada no ambiente nem no arquivo .env.");
    process.exit(1);
  }

  const force = process.argv.includes("--force");
  const filterArg = process.argv.find((a) => a.startsWith("--voice="));
  const onlyVoice = filterArg ? filterArg.split("=")[1]?.trim().toLowerCase() : null;

  fs.mkdirSync(SAMPLES_DIR, { recursive: true });
  const ai = new GoogleGenAI({ apiKey });

  const voicesToGenerate = onlyVoice
    ? GEMINI_OFFICIAL_VOICES.filter((v) => v.name.toLowerCase() === onlyVoice)
    : GEMINI_OFFICIAL_VOICES;

  if (voicesToGenerate.length === 0) {
    console.error(`[ERRO] Nenhuma voz encontrada para o filtro "${onlyVoice}".`);
    process.exit(1);
  }

  console.log(`[ClonaVoz] Gerando amostras estáticas em: ${SAMPLES_DIR}`);
  let generated = 0;
  let skipped = 0;
  let failed = 0;

  for (const voice of voicesToGenerate) {
    const fileName = `${voice.name.toLowerCase()}.wav`;
    const filePath = path.join(SAMPLES_DIR, fileName);

    if (!force && fs.existsSync(filePath) && fs.statSync(filePath).size > 1000) {
      console.log(`[SKIP] ${voice.name} já existe em ${fileName} (custo zero).`);
      skipped++;
      continue;
    }

    const demoText = `Olá! Eu sou a voz ${voice.name} no estúdio ClonaVoz. Esta é uma amostra oficial em alta definição para você testar meu timbre antes de gerar o seu áudio.`;

    try {
      const interaction = await ai.interactions.create({
        model: "gemini-3.8-flash-lite-tts",
        input: [
          {
            type: "text",
            text: demoText,
            annotations: [
              {
                type: "speech_metadata",
                style: voice.defaultStyle
              }
            ]
          }
        ],
        response_format: { type: "audio" },
        generation_config: {
          speech_config: [
            {
              language: "pt-BR",
              voice: voice.name
            }
          ]
        }
      });

      const audioBase64 = interaction.output_audio?.data;
      if (!audioBase64) {
        throw new Error("Resposta sem output_audio.data");
      }

      const wavBuffer = Buffer.from(audioBase64, "base64");
      fs.writeFileSync(filePath, wavBuffer);
      console.log(`[OK] ${voice.name} salvo em ${fileName} (${Math.round(wavBuffer.length / 1024)} KB)`);
      generated++;
    } catch (err) {
      console.error(`[ERRO] Falha ao gerar amostra de ${voice.name}: ${err?.message || err}`);
      failed++;
    }
  }

  console.log(`[Resumo] Geradas: ${generated} | Puladas: ${skipped} | Falhas: ${failed}`);
  if (failed > 0) process.exit(1);
}

main();
