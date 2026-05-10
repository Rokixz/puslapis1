"""
image_slider.py
---------------
Generates a polished, production-ready image slider HTML file.

Usage:
    python image_slider.py                          # uses built-in demo images
    python image_slider.py img1.jpg img2.jpg ...    # your own local images
    python image_slider.py --urls url1 url2 ...     # remote image URLs
    python image_slider.py --output my_slider.html  # custom output filename

Options:
    --output   OUTPUT   Output HTML filename (default: slider.html)
    --title    TITLE    Page / slider title (default: Image Slider)
    --auto     SECS     Auto-play interval in seconds (default: 4, 0 to disable)
    --urls     URLS     Space-separated image URLs (overrides positional args)
    --captions CAPS     Space-separated captions, one per image (quote each)
"""

import argparse
import base64
import os
import sys
import textwrap
from pathlib import Path

# ---------------------------------------------------------------------------
# Demo gradient images (base64 SVG) used when no images are supplied
# ---------------------------------------------------------------------------
DEMO_SLIDES = [
    {
        "src": "data:image/svg+xml;base64,"
        + base64.b64encode(
            b'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="600">'
            b'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
            b'<stop offset="0%" stop-color="#0f0c29"/>'
            b'<stop offset="50%" stop-color="#302b63"/>'
            b'<stop offset="100%" stop-color="#24243e"/></linearGradient></defs>'
            b'<rect width="1200" height="600" fill="url(#g)"/>'
            b'<text x="600" y="310" font-family="Georgia,serif" font-size="72" '
            b'fill="rgba(255,255,255,0.12)" text-anchor="middle">01</text></svg>'
        ).decode(),
        "caption": "Midnight Gradient — Slide One",
    },
    {
        "src": "data:image/svg+xml;base64,"
        + base64.b64encode(
            b'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="600">'
            b'<defs><linearGradient id="g" x1="0" y1="1" x2="1" y2="0">'
            b'<stop offset="0%" stop-color="#11998e"/>'
            b'<stop offset="100%" stop-color="#38ef7d"/></linearGradient></defs>'
            b'<rect width="1200" height="600" fill="url(#g)"/>'
            b'<text x="600" y="310" font-family="Georgia,serif" font-size="72" '
            b'fill="rgba(0,0,0,0.10)" text-anchor="middle">02</text></svg>'
        ).decode(),
        "caption": "Emerald Wave — Slide Two",
    },
    {
        "src": "data:image/svg+xml;base64,"
        + base64.b64encode(
            b'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="600">'
            b'<defs><linearGradient id="g" x1="1" y1="0" x2="0" y2="1">'
            b'<stop offset="0%" stop-color="#f7971e"/>'
            b'<stop offset="100%" stop-color="#ffd200"/></linearGradient></defs>'
            b'<rect width="1200" height="600" fill="url(#g)"/>'
            b'<text x="600" y="310" font-family="Georgia,serif" font-size="72" '
            b'fill="rgba(0,0,0,0.10)" text-anchor="middle">03</text></svg>'
        ).decode(),
        "caption": "Golden Hour — Slide Three",
    },
    {
        "src": "data:image/svg+xml;base64,"
        + base64.b64encode(
            b'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="600">'
            b'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0">'
            b'<stop offset="0%" stop-color="#cb2d3e"/>'
            b'<stop offset="100%" stop-color="#ef473a"/></linearGradient></defs>'
            b'<rect width="1200" height="600" fill="url(#g)"/>'
            b'<text x="600" y="310" font-family="Georgia,serif" font-size="72" '
            b'fill="rgba(255,255,255,0.12)" text-anchor="middle">04</text></svg>'
        ).decode(),
        "caption": "Crimson Dusk — Slide Four",
    },
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def encode_local_image(path: str) -> str:
    """Return a data-URI for a local image file."""
    ext = Path(path).suffix.lower().lstrip(".")
    mime_map = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
        "svg": "image/svg+xml",
    }
    mime = mime_map.get(ext, "image/jpeg")
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{data}"


def build_slides(args) -> list:
    """Return a list of {src, caption} dicts based on CLI arguments."""
    slides = []

    # --- remote URLs ---
    if args.urls:
        sources = args.urls
        captions = args.captions or [""] * len(sources)
        for i, src in enumerate(sources):
            cap = captions[i] if i < len(captions) else ""
            slides.append({"src": src, "caption": cap})
        return slides

    # --- local files (positional args) ---
    if args.images:
        captions = args.captions or [""] * len(args.images)
        for i, img in enumerate(args.images):
            if not os.path.isfile(img):
                print(f"[warning] File not found, skipping: {img}", file=sys.stderr)
                continue
            cap = captions[i] if i < len(captions) else ""
            slides.append({"src": encode_local_image(img), "caption": cap})
        if slides:
            return slides

    # --- fall back to built-in demos ---
    print("[info] No images supplied — using built-in demo slides.", file=sys.stderr)
    if args.captions:
        for i, s in enumerate(DEMO_SLIDES):
            s = dict(s)
            if i < len(args.captions):
                s["caption"] = args.captions[i]
            slides.append(s)
    else:
        slides = list(DEMO_SLIDES)
    return slides


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

def generate_html(slides: list, title: str, auto_ms: int) -> str:
    # Build JS array of slide data
    slides_js = "[\n"
    for s in slides:
        src = s["src"].replace("`", "\\`")
        cap = s["caption"].replace("`", "\\`")
        slides_js += f'        {{ src: `{src}`, caption: `{cap}` }},\n'
    slides_js += "      ]"

    auto_setting = str(auto_ms)

    html = textwrap.dedent(f"""\
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>{title}</title>
      <style>
        /* ── Reset & base ─────────────────────────────── */
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
          min-height: 100vh;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          background: #0d0d0d;
          font-family: 'Georgia', 'Times New Roman', serif;
          color: #f0ebe3;
        }}

        h1 {{
          font-size: clamp(1.1rem, 2.5vw, 1.6rem);
          font-weight: 400;
          letter-spacing: 0.35em;
          text-transform: uppercase;
          color: rgba(240,235,227,0.55);
          margin-bottom: 2.4rem;
        }}

        /* ── Slider wrapper ───────────────────────────── */
        .slider-wrap {{
          position: relative;
          width: min(92vw, 900px);
          aspect-ratio: 16 / 8;
          overflow: hidden;
          border-radius: 4px;
          box-shadow:
            0 2px 4px rgba(0,0,0,.4),
            0 8px 32px rgba(0,0,0,.6),
            0 0 0 1px rgba(255,255,255,.06);
        }}

        /* ── Track (holds all slides side by side) ────── */
        .slider-track {{
          display: flex;
          height: 100%;
          will-change: transform;
          transition: transform 0.72s cubic-bezier(0.77, 0, 0.18, 1);
        }}

        /* ── Individual slide ─────────────────────────── */
        .slide {{
          flex: 0 0 100%;
          position: relative;
          overflow: hidden;
        }}

        .slide img {{
          width: 100%;
          height: 100%;
          object-fit: cover;
          display: block;
          /* Subtle Ken-Burns when active */
          transition: transform 6s ease;
          transform: scale(1.04);
        }}

        .slide.active img {{
          transform: scale(1);
        }}

        /* ── Caption ──────────────────────────────────── */
        .caption {{
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          padding: 2.2rem 2rem 1.4rem;
          background: linear-gradient(transparent, rgba(0,0,0,0.68));
          font-size: clamp(0.78rem, 1.6vw, 1rem);
          letter-spacing: 0.06em;
          color: rgba(255,255,255,0.88);
          opacity: 0;
          transform: translateY(8px);
          transition: opacity 0.5s 0.3s ease, transform 0.5s 0.3s ease;
        }}

        .slide.active .caption {{
          opacity: 1;
          transform: translateY(0);
        }}

        /* ── Prev / Next arrows ───────────────────────── */
        .arrow {{
          position: absolute;
          top: 50%;
          transform: translateY(-50%);
          z-index: 10;
          width: 46px;
          height: 46px;
          border: 1px solid rgba(255,255,255,0.28);
          border-radius: 50%;
          background: rgba(0,0,0,0.35);
          backdrop-filter: blur(6px);
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: background 0.2s, border-color 0.2s, transform 0.2s;
          color: #fff;
          font-size: 1.1rem;
          user-select: none;
        }}
        .arrow:hover {{
          background: rgba(255,255,255,0.18);
          border-color: rgba(255,255,255,0.7);
          transform: translateY(-50%) scale(1.1);
        }}
        .arrow.prev {{ left: 14px; }}
        .arrow.next {{ right: 14px; }}

        /* ── Dot indicators ───────────────────────────── */
        .dots {{
          display: flex;
          gap: 8px;
          margin-top: 1.4rem;
        }}

        .dot {{
          width: 28px;
          height: 3px;
          border-radius: 2px;
          background: rgba(255,255,255,0.22);
          cursor: pointer;
          transition: background 0.3s, transform 0.3s;
        }}
        .dot.active {{
          background: rgba(255,255,255,0.88);
          transform: scaleX(1.18);
        }}

        /* ── Progress bar ─────────────────────────────── */
        .progress {{
          position: absolute;
          bottom: 0;
          left: 0;
          height: 2px;
          background: rgba(255,255,255,0.75);
          width: 0%;
          z-index: 5;
          border-radius: 0 2px 2px 0;
        }}

        /* ── Responsive ───────────────────────────────── */
        @media (max-width: 480px) {{
          .arrow {{ width: 36px; height: 36px; font-size: 0.9rem; }}
        }}
      </style>
    </head>
    <body>

      <h1>{title}</h1>

      <div class="slider-wrap" id="slider">
        <div class="slider-track" id="track"></div>
        <button class="arrow prev" id="prevBtn" aria-label="Previous slide">&#8592;</button>
        <button class="arrow next" id="nextBtn" aria-label="Next slide">&#8594;</button>
        <div class="progress" id="progress"></div>
      </div>

      <div class="dots" id="dots"></div>

      <script>
      (function () {{
        const SLIDES    = {slides_js};
        const AUTO_MS   = {auto_setting};   // 0 = disabled

        const track     = document.getElementById('track');
        const dotsWrap  = document.getElementById('dots');
        const progressEl= document.getElementById('progress');
        let current     = 0;
        let timer       = null;
        let progTimer   = null;

        /* ── Build DOM ── */
        SLIDES.forEach((s, i) => {{
          // Slide
          const slide = document.createElement('div');
          slide.className = 'slide' + (i === 0 ? ' active' : '');

          const img = document.createElement('img');
          img.src = s.src;
          img.alt = s.caption || `Slide ${{i + 1}}`;
          img.loading = i === 0 ? 'eager' : 'lazy';
          slide.appendChild(img);

          if (s.caption) {{
            const cap = document.createElement('div');
            cap.className = 'caption';
            cap.textContent = s.caption;
            slide.appendChild(cap);
          }}

          track.appendChild(slide);

          // Dot
          const dot = document.createElement('button');
          dot.className = 'dot' + (i === 0 ? ' active' : '');
          dot.setAttribute('aria-label', `Go to slide ${{i + 1}}`);
          dot.addEventListener('click', () => goTo(i));
          dotsWrap.appendChild(dot);
        }});

        /* ── Navigate ── */
        function goTo(idx) {{
          const slides = track.querySelectorAll('.slide');
          const dots   = dotsWrap.querySelectorAll('.dot');
          slides[current].classList.remove('active');
          dots[current].classList.remove('active');
          current = (idx + SLIDES.length) % SLIDES.length;
          slides[current].classList.add('active');
          dots[current].classList.add('active');
          track.style.transform = `translateX(${{-current * 100}}%)`;
          if (AUTO_MS) resetProgress();
        }}

        document.getElementById('prevBtn').addEventListener('click', () => goTo(current - 1));
        document.getElementById('nextBtn').addEventListener('click', () => goTo(current + 1));

        /* ── Keyboard ── */
        document.addEventListener('keydown', e => {{
          if (e.key === 'ArrowLeft')  goTo(current - 1);
          if (e.key === 'ArrowRight') goTo(current + 1);
        }});

        /* ── Swipe ── */
        let touchStartX = null;
        const slider = document.getElementById('slider');
        slider.addEventListener('touchstart', e => {{ touchStartX = e.touches[0].clientX; }}, {{passive: true}});
        slider.addEventListener('touchend', e => {{
          if (touchStartX === null) return;
          const dx = e.changedTouches[0].clientX - touchStartX;
          if (Math.abs(dx) > 40) goTo(current + (dx < 0 ? 1 : -1));
          touchStartX = null;
        }}, {{passive: true}});

        /* ── Auto-play & progress bar ── */
        function resetProgress() {{
          clearInterval(timer);
          clearInterval(progTimer);
          progressEl.style.transition = 'none';
          progressEl.style.width = '0%';
          void progressEl.offsetWidth; // reflow
          progressEl.style.transition = `width ${{AUTO_MS}}ms linear`;
          progressEl.style.width = '100%';
          timer = setInterval(() => goTo(current + 1), AUTO_MS);
        }}

        if (AUTO_MS) resetProgress();

        /* Pause on hover */
        slider.addEventListener('mouseenter', () => {{
          clearInterval(timer);
          clearInterval(progTimer);
          progressEl.style.transition = 'none';
        }});
        slider.addEventListener('mouseleave', () => {{
          if (AUTO_MS) resetProgress();
        }});
      }})();
      </script>
    </body>
    </html>
    """)
    return html


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(
        description="Generate a sliding image carousel HTML file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("images", nargs="*", help="Local image file paths")
    p.add_argument("--urls", nargs="+", metavar="URL", help="Remote image URLs")
    p.add_argument("--captions", nargs="+", metavar="CAP", help="Captions (one per slide)")
    p.add_argument("--output", default="slider.html", metavar="FILE", help="Output HTML filename")
    p.add_argument("--title", default="Image Slider", help="Slider title")
    p.add_argument("--auto", type=float, default=4.0, metavar="SECS",
                   help="Auto-play interval in seconds (0 to disable)")
    return p.parse_args()


def main():
    args = parse_args()
    slides = build_slides(args)
    if not slides:
        print("[error] No valid slides could be built. Exiting.", file=sys.stderr)
        sys.exit(1)

    auto_ms = int(args.auto * 1000)
    html = generate_html(slides, args.title, auto_ms)

    out = args.output
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[✓] Slider written to: {os.path.abspath(out)}")
    print(f"    Slides : {len(slides)}")
    print(f"    Auto   : {'disabled' if not auto_ms else f'{args.auto}s'}")
    print(f"\n    Open in your browser: file://{os.path.abspath(out)}")


if __name__ == "__main__":
    main()
