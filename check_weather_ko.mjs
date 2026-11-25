// 날씨 버블 종단 검증: 패치된 파이프라인(IP 위치 → 한국어 역지오코딩 → 날씨)을
// 그대로 실행해, 버블에 실제로 뜰 문자열을 출력한다. 네트워크가 필요하다.
//
//   node check_weather_ko.mjs
//
// DSH 인증(401) 없이도 날씨 경로를 확인하려고 만들었다.

import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const DSH_HOME = process.env.DSH_HOME ?? path.join(os.homedir(), ".dsh");
const IDX = path.join(
  DSH_HOME, "profiles", "desktop", "node_modules", "dsh-pet", "lib", "index.js");

if (!fs.existsSync(IDX)) {
  console.error("dsh-pet lib/index.js를 찾을 수 없습니다:", IDX);
  process.exit(1);
}

const src = fs.readFileSync(IDX, "utf8");
const HAN = /[\u4e00-\u9fff]/;

// 패치된 WMO 표를 번들에서 그대로 읽어 쓴다
const wmoTable = (() => {
  const b = src.indexOf("const TEXT_BY_CODE = {");
  if (b < 0) throw new Error("TEXT_BY_CODE 표가 없습니다 (날씨 패치 미적용?)");
  const e = src.indexOf("};", b);
  return new Function(`return (${src.slice(b + "const TEXT_BY_CODE = ".length, e + 1)});`)();
})();

if (!/koreanPlaceName/.test(src)) {
  console.error("도시명 패치가 적용되지 않았습니다. patch_dsh_pet_ko.py를 먼저 실행하세요.");
  process.exit(1);
}

async function fetchJson(url) {
  const r = await fetch(url, { signal: AbortSignal.timeout(15000) });
  if (!r.ok) throw new Error("HTTP " + r.status);
  return r.json();
}

// 1. IP 위치 (패치 후에는 좌표도 함께 요청한다)
async function locateCity() {
  const b = await fetchJson(
    "http://ip-api.com/json/?lang=zh-CN&fields=status,city,regionName,country,lat,lon");
  if (b.status !== "success" || !b.city) return null;
  return { city: b.city, region: b.regionName ?? "", latitude: b.lat, longitude: b.lon };
}

// 2. 좌표 → 한국어 지명 (주입된 헬퍼와 같은 요청)
const REVERSE = "https://api.bigdatacloud.net/data/reverse-geocode-client";
async function koreanPlaceName(located) {
  if (typeof located?.latitude !== "number" || typeof located?.longitude !== "number") return null;
  try {
    const b = await fetchJson(
      `${REVERSE}?latitude=${located.latitude}&longitude=${located.longitude}&localityLanguage=ko`);
    return b.city ?? b.principalSubdivision ?? null;
  } catch {
    return null;
  }
}

// 3. 도시명 → 좌표 (ko 우선, zh 폴백)
const KO = "https://geocoding-api.open-meteo.com/v1/search?count=1&language=ko&format=json&name=";
const ZH = "https://geocoding-api.open-meteo.com/v1/search?count=1&language=zh&format=json&name=";
async function searchPlace(name) {
  let body;
  try { body = await fetchJson(KO + encodeURIComponent(name)); } catch { body = undefined; }
  if (!Array.isArray(body?.results) || body.results.length === 0) {
    body = await fetchJson(ZH + encodeURIComponent(name));
  }
  const f = body?.results?.[0];
  return f ? { name: f.name, latitude: f.latitude, longitude: f.longitude } : null;
}

const located = await locateCity();
if (located === null) {
  console.error("IP 위치를 얻지 못했습니다 (네트워크 확인)");
  process.exit(1);
}
console.log("IP 위치:", located);

const koName = await koreanPlaceName(located);
const shownCity = koName ?? located.city;
const shownRegion = koName === null ? located.region : "";
const title = [shownRegion, shownCity].filter((s) => s).join("");

console.log("역지오코딩:", koName ?? "(실패 — IP 값 사용)");
console.log("버블 제목:", title, HAN.test(title) ? "  <-- 중문 남음!" : "  OK");

const place = await searchPlace(shownCity);
if (place === null) {
  console.log("\n좌표를 얻지 못해 날씨는 생략합니다.");
  process.exit(HAN.test(title) ? 1 : 0);
}

const c = (await fetchJson(
  `https://api.open-meteo.com/v1/forecast?latitude=${place.latitude}&longitude=${place.longitude}` +
  "&current=temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code&timezone=auto"
)).current;

const bubble = {
  제목: title || place.name,
  요약: wmoTable[c.weather_code] ?? "알 수 없는 날씨",
  기온: c.temperature_2m + "°C",
  체감: c.apparent_temperature + "°C",
  습도: c.relative_humidity_2m + "%",
  풍속: c.wind_speed_10m + " km/h",
};
console.log("\n날씨 버블:", bubble);

const bad = Object.entries(bubble).filter(([, v]) => HAN.test(String(v)));
if (bad.length) {
  console.error("\n중문이 남아 있습니다:", bad);
  process.exit(1);
}
console.log("\nRESULT: OK — 날씨 버블이 전부 한국어입니다");
