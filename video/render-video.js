// Renders services-video.html frame by frame and pipes JPEG frames into ffmpeg with a generated ambient pad.
// Usage: node video/render-video.js land|port <out.mp4> <path-to-ffmpeg>
//   ffmpeg: `pip install imageio-ffmpeg` then python3 -c "import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())"
// Playwright is required (npm i -g playwright); set PLAYWRIGHT_MODULE to its path if it is not resolvable.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const { execFileSync, spawn } = require('child_process');
const [,, o, out, ffmpeg] = process.argv;
const FPS = 30;
(async () => {
  const W = o === 'port' ? 1080 : 1920, H = o === 'port' ? 1920 : 1080;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: W, height: H } });
  await p.route(/fonts\.(googleapis|gstatic)\.com/, r => { const u = r.request().url(); r.fulfill({ status: 200, body: execFileSync('curl', ['-sS', '-A', 'Mozilla/5.0 Chrome/120', u]), contentType: u.includes('googleapis') ? 'text/css' : 'font/woff2' }); });
  await p.goto('file://' + require('path').join(__dirname, 'services-video.html') + `?o=${o}`, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  const D = await p.evaluate(() => window.DURATION);
  const pad = [
    'sin(2*PI*130.81*t)*0.5+sin(2*PI*329.63*t)+sin(2*PI*392.00*t)+sin(2*PI*493.88*t)*0.6',
    'sin(2*PI*174.61*t)*0.5+sin(2*PI*440.00*t)+sin(2*PI*523.25*t)+sin(2*PI*659.25*t)*0.5',
  ];
  const w = '(0.5+0.5*cos(2*PI*t/16))';
  const expr = `0.032*(${w}*(${pad[0]})+(1-${w})*(${pad[1]}))*(0.85+0.15*sin(2*PI*0.2*t))`;
  const ff = spawn(ffmpeg, ['-y', '-loglevel', 'error',
    '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-f', 'lavfi', '-i', `aevalsrc=${expr}:s=44100:d=${D}`,
    '-filter_complex', `[1:a]aecho=0.8:0.7:120|240:0.25|0.15,afade=t=in:st=0:d=2.5,afade=t=out:st=${D - 3}:d=3,volume=8dB[a]`,
    '-map', '0:v', '-map', '[a]',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', String(FPS),
    '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const total = Math.round(D * FPS);
  for (let i = 0; i < total; i++) {
    await p.evaluate(t => render(t), i / FPS);
    const buf = await p.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 360 === 0) console.log(`${o}: frame ${i}/${total}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await b.close();
  console.log(`${o}: done`);
})();
