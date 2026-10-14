/* Final Cut Pro 7 XML (xmeml v4) writer for the Aurobindo timeline.
   Premiere Pro (File > Import) and DaVinci Resolve (File > Import > Timeline) both read it.
   Paths are relative to video/aurobindo/ under ROOT; the NLE asks to relink once, point it at that folder.
   Used by editor/index.html (Export) and by `node editor/xmeml.js` (writes editor/Aurobindo_timeline.xml). */
(function (global) {
	const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
	const rate = (fps) => `<rate><timebase>${fps}</timebase><ntsc>FALSE</ntsc></rate>`;

	/** Greedy lane packing so no two clips overlap on one NLE track. */
	function lanes(items) {
		const out = [];
		[...items].sort((a, b) => a.s - b.s).forEach((it) => {
			let lane = out.find((l) => l[l.length - 1].e <= it.s + 1e-6);
			if (!lane) out.push((lane = []));
			lane.push(it);
		});
		return out;
	}

	function buildXML(p, opts = {}) {
		const fps = p.fps;
		const root = (opts.root || 'file://localhost/aurobindo').replace(/\/$/, '');
		const F = (sec) => Math.round(sec * fps);
		const total = F(p.duration);
		const files = new Map();
		let uid = 0;

		function fileRef(path, durSec, kind) {
			if (files.has(path)) return `<file id="${files.get(path)}"/>`;
			const id = `file-${++uid}`;
			files.set(path, id);
			const media = kind === 'video'
				? `<media><video><samplecharacteristics>${rate(fps)}<width>${p.width}</width><height>${p.height}</height></samplecharacteristics></video></media>`
				: `<media><audio><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate></samplecharacteristics><channelcount>2</channelcount></audio></media>`;
			return `<file id="${id}"><name>${esc(path.split('/').pop())}</name><pathurl>${esc(root + '/' + path)}</pathurl>${rate(fps)}<duration>${F(durSec)}</duration>${media}</file>`;
		}

		const level = (db) => `<filter><effect><name>Audio Levels</name><effectid>audiolevels</effectid><effectcategory>audiolevels</effectcategory><effecttype>audiolevels</effecttype><mediatype>audio</mediatype><parameter><parameterid>level</parameterid><name>Level</name><valuemin>0</valuemin><valuemax>3.98109</valuemax><value>${Math.pow(10, db / 20).toFixed(5)}</value></parameter></effect></filter>`;

		function clip(kind, name, path, srcDur, s, e, inSec, extra = '') {
			const st = F(s), en = F(e), i = F(inSec);
			return `<clipitem id="clip-${++uid}"><name>${esc(name)}</name><enabled>TRUE</enabled><duration>${F(srcDur)}</duration>${rate(fps)}<start>${st}</start><end>${en}</end><in>${i}</in><out>${i + en - st}</out>${fileRef(path, srcDur, kind)}${kind === 'audio' ? '<sourcetrack><mediatype>audio</mediatype><trackindex>1</trackindex></sourcetrack>' : ''}${extra}</clipitem>`;
		}

		// video: B-roll lanes at the bottom, the finished render on top as the reference picture (toggle it off to see raw B-roll)
		const vTracks = lanes(p.video.find((t) => t.key === 'broll').items).map((lane) =>
			`<track>${lane.map((it) => clip('video', it.label, 'public/' + it.src, Math.max(it.srcDur || 0, it.trim + it.e - it.s), it.s, it.e, it.trim || 0)).join('')}</track>`);
		vTracks.push(`<track>${clip('video', 'FINAL RENDER (reference)', p.render, p.duration, 0, p.duration, 0)}</track>`);

		const aTracks = p.audio.map((a) =>
			`<track>${a.muted ? '' : clip('audio', a.name, 'editor/data/' + a.file, p.duration, 0, p.duration, 0)}</track>`);
		lanes(p.sfx.filter((c) => !c.muted)).forEach((lane) =>
			aTracks.push(`<track>${lane.map((c) => clip('audio', c.label, 'editor/data/' + c.file, c.len, c.s, c.e, 0, level(c.gain + 3))).join('')}</track>`));

		const markers = [
			...p.scenes.map((s) => `<marker><name>${esc(s.id.toUpperCase())}</name><comment>scene</comment><in>${F(s.s)}</in><out>-1</out></marker>`),
			...p.video.find((t) => t.key === 'title').items.map((t) => `<marker><name>${esc(t.label)}</name><comment>title</comment><in>${F(t.s)}</in><out>-1</out></marker>`),
		].join('');

		return `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="4"><sequence id="seq-1"><name>${esc(p.title)}</name><duration>${total}</duration>${rate(fps)}
<timecode>${rate(fps)}<string>00:00:00:00</string><frame>0</frame><displayformat>NDF</displayformat></timecode>
<media><video><format><samplecharacteristics>${rate(fps)}<width>${p.width}</width><height>${p.height}</height><pixelaspectratio>square</pixelaspectratio></samplecharacteristics></format>
${vTracks.join('\n')}</video>
<audio><numOutputChannels>2</numOutputChannels>
${aTracks.join('\n')}</audio></media>
${markers}</sequence></xmeml>
`;
	}

	global.buildXML = buildXML;
	if (typeof module !== 'undefined' && module.exports) {
		module.exports = {buildXML};
		if (require.main === module) {
			const fs = require('fs'), path = require('path');
			const p = JSON.parse(fs.readFileSync(path.join(__dirname, 'data/project.json'), 'utf8'));
			fs.writeFileSync(path.join(__dirname, 'Aurobindo_timeline.xml'), buildXML(p));
			console.log('wrote editor/Aurobindo_timeline.xml');
		}
	}
})(typeof window !== 'undefined' ? window : globalThis);
