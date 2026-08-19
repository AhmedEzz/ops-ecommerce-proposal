#!/usr/bin/env node
/**
 * Convert the Markdown technical proposal into a client-ready Word document.
 *
 * pandoc is not available on this machine, so this is a purpose-built converter
 * covering exactly the Markdown subset the proposal uses: ATX headings, GFM
 * tables with alignment, bullet and numbered lists, fenced code, horizontal
 * rules, images, and inline bold / italic / code / links.
 *
 * Diagrams are authored as SVG for the Markdown and HTML deliverables; Word
 * cannot embed SVG reliably, so image paths are swapped to the 2x PNG renders
 * and scaled to fit the text block.
 */

const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType, ShadingType: _S,
  ImageRun, PageBreak, TableOfContents, Header, Footer, PageNumber,
  LevelFormat, convertInchesToTwip,
} = require('docx');

const ROOT = path.resolve(__dirname, '..');
const SRC = path.join(ROOT, 'deliverables', '01-Technical-Proposal.md');
const OUT = path.join(ROOT, 'deliverables', '01-Technical-Proposal.docx');
const DIAGRAMS = path.join(ROOT, 'deliverables', 'diagrams');

/* ---- page geometry (US Letter, 1" margins) ---- */
const PAGE_W = 12240, PAGE_H = 15840, MARGIN = 1440;
const CONTENT_DXA = PAGE_W - MARGIN * 2;          // 9360 dxa == 6.5"
const CONTENT_PX = 624;                            // 6.5" at 96dpi
const MAX_IMG_H = 780;                             // keep a figure on one page

const INK = '1F2937', MUTED = '6B7280', BRAND = '4F46E5', LINE = 'D1D5DB';

/* ---------- PNG dimensions, read straight from the IHDR chunk ---------- */
function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}

/* ---------- inline markdown -> TextRun[] ---------- */
function inline(text, base = {}) {
  const runs = [];
  // Ordered so ** is consumed before *, and links before plain text.
  const re = /(\*\*[^*]+\*\*)|(`[^`]+`)|(\*[^*\n]+\*)|(\[[^\]]+\]\([^)]+\))/g;
  let last = 0, m;
  const push = (t, opts) => { if (t) runs.push(new TextRun({ text: t, ...base, ...opts })); };

  while ((m = re.exec(text)) !== null) {
    push(text.slice(last, m.index));
    const tok = m[0];
    if (m[1]) push(tok.slice(2, -2), { bold: true });
    else if (m[2]) push(tok.slice(1, -1), { font: 'Consolas', size: 18, color: BRAND });
    else if (m[3]) push(tok.slice(1, -1), { italics: true });
    else if (m[4]) {
      const label = tok.slice(1, tok.indexOf(']'));
      push(label, { color: BRAND });           // rendered as styled text, not a hyperlink field
    }
    last = m.index + tok.length;
  }
  push(text.slice(last));
  return runs.length ? runs : [new TextRun({ text: '', ...base })];
}

/* ---------- block helpers ---------- */
const para = (text, opts = {}) => new Paragraph({
  children: inline(text, opts.run || {}),
  spacing: { before: opts.before ?? 0, after: opts.after ?? 120, line: 276 },
  alignment: opts.align,
  ...(opts.border ? { border: opts.border } : {}),
});

function heading(text, level) {
  const map = { 1: HeadingLevel.HEADING_1, 2: HeadingLevel.HEADING_1,
                3: HeadingLevel.HEADING_2, 4: HeadingLevel.HEADING_3 };
  return new Paragraph({
    children: inline(text.replace(/`/g, '')),
    heading: map[level] || HeadingLevel.HEADING_3,
    spacing: { before: level <= 2 ? 320 : 260, after: 140 },
    keepNext: true,
  });
}

function image(file, caption) {
  const png = path.join(DIAGRAMS, path.basename(file).replace(/\.svg$/, '.png'));
  if (!fs.existsSync(png)) return [para(`[missing diagram: ${path.basename(png)}]`)];
  const { w, h } = pngSize(png);
  let dw = CONTENT_PX, dh = Math.round((h / w) * CONTENT_PX);
  if (dh > MAX_IMG_H) { dh = MAX_IMG_H; dw = Math.round((w / h) * MAX_IMG_H); }
  return [new Paragraph({
    children: [new ImageRun({ type: 'png', data: fs.readFileSync(png),
                              transformation: { width: dw, height: dh } })],
    alignment: AlignmentType.CENTER,
    spacing: { before: 160, after: 60 },
  })];
}

/* ---------- GFM table -> docx Table ---------- */
function buildTable(rows, aligns) {
  const cols = Math.max(...rows.map(r => r.length));
  // Weight columns by the longest cell, clamped so one long column cannot
  // squeeze the others to nothing.
  const weights = Array.from({ length: cols }, (_, i) =>
    Math.min(46, Math.max(7, ...rows.map(r => (r[i] || '').replace(/[*`]/g, '').length))));
  const total = weights.reduce((a, b) => a + b, 0);
  const widths = weights.map(w => Math.round((w / total) * CONTENT_DXA));
  widths[cols - 1] += CONTENT_DXA - widths.reduce((a, b) => a + b, 0); // absorb rounding

  const align = i => aligns[i] === 'right' ? AlignmentType.RIGHT
                   : aligns[i] === 'center' ? AlignmentType.CENTER : AlignmentType.LEFT;

  const cell = (text, i, isHead) => new TableCell({
    width: { size: widths[i], type: WidthType.DXA },
    shading: isHead ? { type: ShadingType.CLEAR, fill: 'EEF2FF', color: 'auto' } : undefined,
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    children: [new Paragraph({
      children: inline(text || '', isHead ? { bold: true, size: 17, color: INK } : { size: 18 }),
      alignment: align(i),
      spacing: { before: 0, after: 0, line: 240 },
    })],
  });

  return new Table({
    columnWidths: widths,
    width: { size: CONTENT_DXA, type: WidthType.DXA },
    borders: ['top', 'bottom', 'left', 'right', 'insideHorizontal', 'insideVertical']
      .reduce((o, k) => (o[k] = { style: BorderStyle.SINGLE, size: 2, color: LINE }, o), {}),
    rows: rows.map((r, ri) => new TableRow({
      tableHeader: ri === 0,
      children: Array.from({ length: cols }, (_, ci) => cell(r[ci], ci, ri === 0)),
    })),
  });
}

const splitRow = line =>
  line.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(s => s.trim());

/* ---------- parse the document ---------- */
function convert(md) {
  const lines = md.split('\n');
  const out = [];
  let i = 0;

  // The Markdown carries a hand-written contents list; Word gets a real TOC field.
  const tocStart = lines.findIndex(l => /^## Table of Contents/.test(l));
  if (tocStart !== -1) {
    let end = tocStart + 1;
    while (end < lines.length && !/^---\s*$/.test(lines[end])) end++;
    lines.splice(tocStart, end - tocStart + 1);
  }

  while (i < lines.length) {
    const line = lines[i];

    if (!line.trim()) { i++; continue; }

    const h = line.match(/^(#{1,6})\s+(.*)$/);
    if (h) { out.push(heading(h[2], h[1].length)); i++; continue; }

    if (/^---+\s*$/.test(line)) {
      out.push(new Paragraph({
        text: '', spacing: { before: 80, after: 160 },
        border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: LINE } },
      }));
      i++; continue;
    }

    const img = line.match(/^!\[(.*?)\]\((.*?)\)/);
    if (img) { out.push(...image(img[2], img[1])); i++; continue; }

    if (line.startsWith('```')) {
      const code = [];
      i++;
      while (i < lines.length && !lines[i].startsWith('```')) code.push(lines[i++]);
      i++;
      code.forEach((c, ix) => out.push(new Paragraph({
        children: [new TextRun({ text: c || ' ', font: 'Consolas', size: 17, color: INK })],
        shading: { type: ShadingType.CLEAR, fill: 'F3F4F6', color: 'auto' },
        spacing: { before: ix === 0 ? 100 : 0, after: ix === code.length - 1 ? 140 : 0, line: 240 },
        indent: { left: 180 },
      })));
      continue;
    }

    if (line.startsWith('|')) {
      const block = [];
      while (i < lines.length && lines[i].startsWith('|')) block.push(lines[i++]);
      const rows = block.map(splitRow);
      let aligns = [];
      // Separator cells may be as short as ":-:" for a centred column.
      if (rows[1] && rows[1].every(c => /^:?-+:?$/.test(c))) {
        aligns = rows[1].map(c => c.endsWith(':') ? (c.startsWith(':') ? 'center' : 'right') : 'left');
        rows.splice(1, 1);
      }
      out.push(buildTable(rows, aligns));
      out.push(new Paragraph({ text: '', spacing: { after: 160 } }));
      continue;
    }

    const bullet = line.match(/^[-*]\s+(.*)$/);
    if (bullet) {
      const text = [bullet[1]];
      i++;
      while (i < lines.length && /^\s{2,}\S/.test(lines[i])) text.push(lines[i++].trim());
      out.push(new Paragraph({
        children: inline(text.join(' ')),
        numbering: { reference: 'bullets', level: 0 },
        spacing: { after: 70, line: 264 },
      }));
      continue;
    }

    const num = line.match(/^(\d+)\.\s+(.*)$/);
    if (num) {
      const text = [num[2]];
      i++;
      while (i < lines.length && /^\s{3,}\S/.test(lines[i])) text.push(lines[i++].trim());
      out.push(new Paragraph({
        children: inline(text.join(' ')),
        numbering: { reference: 'numbers', level: 0 },
        spacing: { after: 70, line: 264 },
      }));
      continue;
    }

    // Plain paragraph: join wrapped source lines until a blank or a new block.
    const buf = [line.trim()];
    i++;
    while (i < lines.length && lines[i].trim() &&
           !/^([-*]\s|\d+\.\s|#{1,6}\s|\||```|!\[|---+\s*$)/.test(lines[i])) {
      buf.push(lines[i++].trim());
    }
    const text = buf.join(' ');
    // A lone *italic* line following an image is its caption.
    const isCaption = /^\*[^*].*\*$/.test(text);
    out.push(new Paragraph({
      children: inline(text, isCaption ? { italics: true, size: 17, color: MUTED } : {}),
      alignment: isCaption ? AlignmentType.CENTER : undefined,
      spacing: { after: isCaption ? 200 : 130, line: 276 },
    }));
  }
  return out;
}

/* ---------- title page ---------- */
function titlePage() {
  const t = (text, opts) => new Paragraph({
    children: [new TextRun({ text, ...opts })],
    alignment: AlignmentType.CENTER,
    spacing: opts.spacing || { after: 120 },
  });
  return [
    new Paragraph({ text: '', spacing: { after: 2400 } }),
    t('Operations Management System', { bold: true, size: 52, color: INK }),
    t('Technical Proposal', { size: 34, color: BRAND, spacing: { after: 80 } }),
    t('High-Level Design · Low-Level Design · Delivery Plan', { size: 22, color: MUTED, spacing: { after: 900 } }),
    t('Prepared for Marketplace Operations', { size: 22, color: INK }),
    t('Version 1.0 · 8 August 2026', { size: 22, color: MUTED, spacing: { after: 600 } }),
    t('Target go-live: 20 November 2026', { bold: true, size: 24, color: INK }),
    t('Seven days before Black Friday, 27 November 2026', { size: 20, color: MUTED }),
    new Paragraph({ children: [new PageBreak()] }),
  ];
}

function tocPage() {
  return [
    new Paragraph({
      children: [new TextRun({ text: 'Contents', bold: true, size: 32, color: INK })],
      spacing: { after: 240 },
    }),
    new TableOfContents('Contents', { hyperlink: true, headingStyleRange: '1-3' }),
    new Paragraph({
      children: [new TextRun({
        text: 'Right-click the table above and choose "Update Field" to populate page numbers.',
        italics: true, size: 17, color: MUTED })],
      spacing: { before: 240 },
    }),
    new Paragraph({ children: [new PageBreak()] }),
  ];
}

/* ---------- build ---------- */
const body = convert(fs.readFileSync(SRC, 'utf8'));

const doc = new Document({
  creator: 'Operations Management System proposal',
  title: 'Operations Management System — Technical Proposal',
  description: 'HLD, LLD, hosting comparison, delivery plan and requirements traceability',
  styles: {
    default: {
      document: { run: { font: 'Calibri', size: 21, color: INK } },
      heading1: { run: { font: 'Calibri', size: 32, bold: true, color: INK },
                  paragraph: { spacing: { before: 360, after: 160 } } },
      heading2: { run: { font: 'Calibri', size: 25, bold: true, color: BRAND },
                  paragraph: { spacing: { before: 300, after: 130 } } },
      heading3: { run: { font: 'Calibri', size: 22, bold: true, color: INK },
                  paragraph: { spacing: { before: 240, after: 110 } } },
    },
  },
  numbering: {
    config: [
      { reference: 'bullets', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•',
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 360, hanging: 220 } } } }] },
      { reference: 'numbers', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.',
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 400, hanging: 260 } } } }] },
    ],
  },
  sections: [{
    properties: {
      page: { size: { width: PAGE_W, height: PAGE_H },
              margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN } },
    },
    headers: {
      default: new Header({ children: [new Paragraph({
        children: [new TextRun({ text: 'Operations Management System — Technical Proposal',
                                 size: 16, color: MUTED })],
        alignment: AlignmentType.RIGHT,
        border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: LINE } },
      })] }),
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        children: [new TextRun({ text: 'Page ', size: 16, color: MUTED }),
                   new TextRun({ children: [PageNumber.CURRENT], size: 16, color: MUTED })],
        alignment: AlignmentType.CENTER,
      })] }),
    },
    children: [...titlePage(), ...tocPage(), ...body],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUT, buf);
  const imgs = (fs.readFileSync(SRC, 'utf8').match(/!\[.*?\]\(diagrams\//g) || []).length;
  console.log(`wrote ${path.relative(ROOT, OUT)}  (${(buf.length / 1024 / 1024).toFixed(2)} MB)`);
  console.log(`  blocks   ${body.length}`);
  console.log(`  diagrams ${imgs} embedded as PNG`);
});
