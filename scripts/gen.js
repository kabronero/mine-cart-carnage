#!/usr/bin/env node
// Generate a single image via Gemini 2.5 Flash Image (Nano Banana).
// Usage: GOOGLE_AI_API_KEY=... node gen.js "prompt text" out/path.png
const fs = require('fs');
const path = require('path');
const https = require('https');

const KEY = process.env.GOOGLE_AI_API_KEY;
if (!KEY){
    console.error('GOOGLE_AI_API_KEY env var not set');
    process.exit(1);
}

const [,, prompt, outFile] = process.argv;
if (!prompt || !outFile){
    console.error('Usage: node gen.js "prompt" out/path.png');
    process.exit(1);
}

const MODEL = process.env.GEMINI_MODEL || 'nano-banana-pro-preview';
const body = JSON.stringify({
    contents: [{ parts: [{ text: prompt }] }],
    generationConfig: { responseModalities: ['IMAGE', 'TEXT'] },
});

const req = https.request({
    hostname: 'generativelanguage.googleapis.com',
    path: `/v1beta/models/${MODEL}:generateContent?key=${KEY}`,
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
    },
}, (res) => {
    const chunks = [];
    res.on('data', (c) => chunks.push(c));
    res.on('end', () => {
        const raw = Buffer.concat(chunks).toString('utf8');
        if (res.statusCode !== 200){
            console.error(`HTTP ${res.statusCode}`);
            console.error(raw.slice(0, 2000));
            process.exit(2);
        }
        let json;
        try { json = JSON.parse(raw); }
        catch (e){ console.error('Bad JSON:', e.message); console.error(raw.slice(0, 800)); process.exit(3); }
        const parts = json?.candidates?.[0]?.content?.parts || [];
        const img = parts.find(p => p.inlineData);
        if (!img){
            console.error('No image in response. Parts:', JSON.stringify(parts, null, 2));
            process.exit(4);
        }
        const buf = Buffer.from(img.inlineData.data, 'base64');
        fs.mkdirSync(path.dirname(outFile), { recursive: true });
        fs.writeFileSync(outFile, buf);
        const text = parts.find(p => p.text)?.text;
        if (text) console.log('Model note:', text.slice(0, 200));
        console.log(`✓ ${outFile} (${(buf.length/1024).toFixed(1)} KB)`);
    });
});
req.on('error', (e) => { console.error('Request error:', e.message); process.exit(5); });
req.write(body);
req.end();
