import { toOut } from "./timeline";

// Romanised Hinglish transcript with word timings (source seconds),
// from faster-whisper (medium) and corrected by hand.
// [text, start, end, keyword?]
type Raw = [string, number, number, 1?];

const RAW: Raw[] = [
  ["Kya", 0.4, 0.7], ["aapne", 0.7, 0.98], ["life", 0.98, 1.22], ["mein", 1.22, 1.36],
  ["kabhi", 1.36, 1.54], ["aisa", 1.54, 1.76], ["shortcut", 1.76, 2.18, 1], ["liya", 2.18, 2.64],
  ["hai,", 2.64, 2.82], ["jo", 2.82, 2.96], ["life", 2.96, 3.28], ["mein", 3.28, 3.44],
  ["aapko", 3.44, 3.8], ["bhaari", 3.8, 4.22, 1], ["pad", 4.22, 4.45, 1], ["gaya", 4.45, 4.68, 1],
  ["ho?", 4.68, 5.38],
  ["Toh", 5.5, 5.68], ["chalo,", 5.68, 6.2], ["aapko", 6.52, 6.8], ["ek", 6.8, 6.98],
  ["story", 6.98, 7.26, 1], ["sunata", 7.26, 7.66], ["hoon.", 7.66, 8.2],
  ["Saal", 8.56, 8.98], ["2011", 8.98, 9.38, 1], ["mein", 9.38, 9.84], ["ek", 9.84, 10.04],
  ["company", 10.04, 10.42], ["thi,", 10.42, 10.64], ["billion", 11.2, 11.9, 1],
  ["dollar", 11.9, 12.4, 1], ["brand,", 12.4, 13.26, 1], ["poori", 13.38, 13.72],
  ["duniya", 13.72, 14.08], ["jaanti", 14.08, 14.4], ["thi.", 14.4, 14.76],
  ["Har", 15.3, 15.66], ["ek", 15.66, 15.96], ["cheez", 15.96, 16.12], ["sell", 16.12, 16.42, 1],
  ["ho", 16.42, 16.64], ["rahi", 16.64, 16.7], ["thi", 16.7, 16.8], ["unki,", 16.8, 17.54],
  ["clothes,", 17.64, 18.16, 1], ["electronics,", 18.32, 19.22, 1], ["furniture,", 19.3, 20.42, 1],
  ["saara", 20.52, 20.8], ["kuch.", 20.8, 21.54],
  ["Aur", 21.84, 22.02], ["ek", 22.02, 22.2], ["din", 22.2, 22.44], ["Google", 22.44, 22.84, 1],
  ["ne", 22.84, 23.48], ["practically", 23.48, 24.32], ["apni", 24.32, 24.66],
  ["top", 24.66, 24.94, 1], ["ranking", 24.94, 25.3, 1], ["se", 25.3, 25.42],
  ["hata", 25.42, 25.72, 1], ["diya.", 25.72, 25.96, 1],
  ["Website", 26.54, 27.04], ["thi,", 27.04, 27.38], ["content", 27.72, 28.26], ["tha,", 28.26, 28.78],
  ["products", 28.88, 29.28], ["the.", 29.28, 29.7],
  ["Aur", 30.3, 30.58], ["Google", 30.58, 31.06, 1], ["ke", 31.06, 31.5], ["front", 31.5, 31.92],
  ["pages", 31.92, 32.38], ["pe", 32.38, 32.9], ["achaanak", 32.9, 33.5], ["se", 33.5, 33.8],
  ["gone.", 34.36, 34.84, 1],
  ["Kyun", 36.1, 36.42, 1], ["hua", 36.42, 36.7], ["ye?", 36.7, 37.5],
  ["Kyunki", 37.9, 38.66], ["unhone", 38.66, 39.56], ["SEO", 39.56, 40.16, 1], ["mein", 40.16, 40.66],
  ["cheating", 40.66, 41.16, 1], ["ki.", 41.16, 41.54],
  ["Unhone", 41.74, 42.24], ["aisi", 42.24, 42.54], ["techniques", 42.54, 42.88],
  ["apnaayi", 42.88, 43.42], ["jo", 43.42, 43.96], ["Google", 43.96, 44.44, 1], ["ke", 44.44, 44.56],
  ["algorithm", 44.56, 45.22, 1], ["ke", 45.22, 45.62], ["khilaaf", 45.62, 46.04, 1], ["thi.", 46.04, 46.58],
  ["Aur", 46.8, 46.94], ["Google", 46.94, 47.34, 1], ["ne", 47.34, 48.4], ["pakad", 48.4, 48.72, 1],
  ["liya.", 48.72, 49.3, 1],
  ["Woh", 49.6, 49.98], ["company", 49.98, 50.38], ["thi", 50.38, 50.86], ["JCPenney,", 50.86, 52.3, 1],
  ["ek", 52.64, 53.06], ["American", 53.06, 53.72, 1], ["retail", 53.72, 54.18, 1], ["giant.", 54.18, 55.02, 1],
  ["Aur", 55.08, 55.84], ["aaj", 55.84, 56.22], ["bhi", 56.22, 56.64], ["ye", 56.64, 56.96],
  ["story", 56.96, 57.36], ["is", 57.36, 57.68], ["industry", 57.68, 58.1], ["mein", 58.1, 58.52],
  ["sabse", 58.52, 58.9, 1], ["bada", 58.9, 59.24, 1], ["lesson", 59.24, 59.52, 1], ["hai.", 59.52, 60.1],
  ["Toh", 60.3, 60.52], ["aaj", 60.52, 60.86], ["ki", 60.86, 60.96], ["video", 60.96, 61.28],
  ["mein,", 61.28, 61.6], ["main", 61.72, 61.78], ["tumhe", 61.78, 62.0], ["woh", 62.0, 62.22],
  ["sab", 62.22, 62.38], ["bataunga", 62.38, 63.14, 1], ["jo", 63.14, 63.52], ["zyaadatar", 63.52, 64.08],
  ["log", 64.08, 64.56], ["sirf", 64.56, 65.08], ["define", 65.08, 65.52, 1], ["karke", 65.52, 65.74],
  ["chhod", 65.74, 65.96], ["dete", 65.96, 66.28], ["hain.", 66.28, 67.02],
  ["Types", 67.02, 67.42, 1], ["of", 67.42, 67.56, 1], ["SEO,", 67.56, 68.44, 1],
  ["with", 68.72, 69.4], ["real", 69.4, 69.68, 1], ["story,", 69.68, 70.14, 1], ["real", 70.42, 70.8, 1],
  ["example,", 70.8, 71.46, 1], ["no", 71.8, 72.06], ["complex", 72.06, 72.7],
  ["sentences,", 72.7, 73.6], ["no", 73.6, 73.88], ["definitions,", 73.88, 74.7], ["no", 74.8, 75.04],
  ["ratta", 75.04, 75.44, 1], ["maaro", 75.44, 75.62, 1], ["theory.", 75.62, 76.08, 1],
  ["Toh", 76.64, 76.86], ["chaliye", 76.86, 77.2], ["shuru", 77.2, 77.42, 1], ["karte", 77.42, 77.72, 1],
  ["hain!", 77.72, 77.94, 1],
];

export type Word = { text: string; start: number; end: number; keyword: boolean };
export type Page = { start: number; end: number; words: Word[] };

// Words in output seconds.
export const WORDS: Word[] = RAW.map(([text, s, e, k]) => ({
  text,
  start: toOut(s),
  end: toOut(e),
  keyword: k === 1,
}));

const MAX_WORDS = 4;
const MAX_CHARS = 24;

// Group words into short caption pages, breaking on punctuation,
// pauses, and length.
const buildPages = (): Page[] => {
  const pages: Page[] = [];
  let cur: Word[] = [];
  const flush = () => {
    if (cur.length === 0) return;
    pages.push({ start: cur[0].start, end: cur[cur.length - 1].end, words: cur });
    cur = [];
  };
  WORDS.forEach((w, i) => {
    const next = WORDS[i + 1];
    const chars = cur.reduce((n, x) => n + x.text.length + 1, 0) + w.text.length;
    if (cur.length >= MAX_WORDS || (cur.length > 0 && chars > MAX_CHARS)) flush();
    cur.push(w);
    const endsSentence = /[.?!,]$/.test(w.text);
    const gap = next ? next.start - w.end : 1;
    if (endsSentence || gap > 0.3) flush();
  });
  flush();
  // Hold each page until the next one starts (max 0.6s) so text doesn't flicker.
  return pages.map((p, i) => {
    const next = pages[i + 1];
    const hold = next ? Math.min(next.start, p.end + 0.6) : p.end + 0.6;
    return { ...p, end: hold };
  });
};

export const PAGES = buildPages();
