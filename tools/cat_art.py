"""Original SVG cat rig: smoky fur, amber eyes, and a battered black hat."""
import math


def cat(phase=0.0, walking=False, blink=False, talking=False, left=False):
    swing = math.sin(phase)
    bob = abs(swing)*2.5 if walking else math.sin(phase)*1.1
    legs = []
    for x, offset, far in [(137, math.pi, True), (229, 0, True), (114, 0, False), (208, math.pi, False)]:
        angle = math.sin(phase+offset)*19 if walking else 0
        fur = '#303b39' if far else 'url(#fur)'
        legs.append(f'''<g transform="rotate({angle} {x} 175)">
          <path d="M{x-12} 168 Q{x-18} 193 {x-10} 218 Q{x-18} 226 {x-14} 232
          Q{x} 238 {x+19} 231 Q{x+23} 224 {x+9} 220 L{x+15} 175Z" fill="{fur}"/>
          <path d="M{x-10} 216l7 5 6-3 6 4" fill="none" stroke="#718078" stroke-width="1.5"/>
          <path d="M{x+5} 227v5m6-5v4" fill="none" stroke="#182522" stroke-width="1.6"/>
        </g>''')
    if blink:
        eyes = '<path d="M235 112q11 8 22-1m20-1q10 7 19-4" fill="none" stroke="#dfc87e" stroke-width="2.4"/>'
    else:
        eyes = '''<path d="M232 107 Q246 98 260 109 Q250 124 237 116Z" fill="url(#amber)" stroke="#1c2623" stroke-width="2.3"/>
          <path d="M274 108 Q286 96 299 103 Q296 117 282 119Z" fill="url(#amber)" stroke="#1c2623" stroke-width="2.3"/>
          <path d="M248 102q-5 11 1 17q5-10-1-17m40-2q-5 10 0 17q5-10 0-17" fill="#111d1a" stroke="none"/>
          <circle cx="243" cy="107" r="2.1" fill="#fff4c6" stroke="none"/>
          <circle cx="284" cy="104" r="1.8" fill="#fff4c6" stroke="none"/>'''
    mouth = ('<path d="M261 139q10-2 13 1q-3 12-10 9Z" fill="#17241f"/><path d="M265 146h6" stroke="#ba8d8b" stroke-width="2"/>' if talking else '<path d="M266 135v6q-6 5-11 0m11 0q6 4 11-2" fill="none" stroke="#25342e" stroke-width="1.8"/>')
    flip = 'translate(360 0) scale(-1 1)' if left else ''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="360" height="260" viewBox="0 0 360 260">
      <defs>
        <linearGradient id="fur" x1="0" y1="0" x2=".6" y2="1"><stop stop-color="#737e76"/><stop offset=".4" stop-color="#4c5953"/><stop offset="1" stop-color="#303e38"/></linearGradient>
        <linearGradient id="ruff" x1="0" y1="0" x2=".3" y2="1"><stop stop-color="#a5a99a"/><stop offset=".5" stop-color="#7c887b"/><stop offset="1" stop-color="#495c50"/></linearGradient>
        <linearGradient id="hat" x1="0" y1="0" x2=".8" y2="1"><stop stop-color="#424b44"/><stop offset=".3" stop-color="#242d28"/><stop offset="1" stop-color="#111d18"/></linearGradient>
        <linearGradient id="amber" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#ae873b"/><stop offset=".6" stop-color="#dfc466"/><stop offset="1" stop-color="#eee3a0"/></linearGradient>
      </defs>
      <g transform="{flip}" stroke="#8b9886" stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round">
      <ellipse cx="180" cy="241" rx="116" ry="8" fill="#344d3c" opacity=".25" stroke="none"/>
      <g transform="translate(0 {-bob})">
        <g transform="rotate({swing*7} 104 147)">
          <path d="M112 145 C75 149 54 124 56 100 C57 77 27 69 23 91 C18 112 40 109 40 128
          L34 124 L39 137 L32 135 Q57 173 107 174Z" fill="url(#fur)"/>
          <path d="M88 156 Q49 145 49 116 Q49 89 32 88" fill="none" stroke="#8f998a" opacity=".6" stroke-width="2"/>
          <path d="M43 143l10 2-2-8m9 18 11 1-4-7" fill="none" stroke="#a0a392" opacity=".45"/>
        </g>
        {''.join(legs[:2])}
        <path d="M92 145 Q91 113 126 111 Q145 103 179 113 Q215 100 237 129
        Q254 155 233 181 L237 191 225 188 219 198 208 190 Q177 209 142 194
        L132 201 128 192 116 196 117 188 Q89 183 92 145Z" fill="url(#fur)"/>
        <path d="M114 127q28-13 53-5m-50 6 8 9-15 5m40-20 8 14-13 7" fill="none" stroke="#253d32" stroke-width="6" opacity=".55"/>
        <path d="M105 166q19 18 50 16m17 3 9-7m-56-62 8-3" fill="none" stroke="#929e8a" opacity=".5"/>
        {''.join(legs[2:])}
        <path d="M216 127 L194 150 203 151 191 171 201 170 197 188 211 182
        L215 201 226 186 237 194 239 176 252 178 248 158 257 156 243 129Z" fill="url(#ruff)"/>
        <path d="M214 150l-4 17 8-5 3 17 5-18m11-9-3 15" fill="none" stroke="#bcc0a9" opacity=".55"/>
        <path d="M219 148q19 10 33-2l-1 8q-17 10-32 1Z" fill="#314e3c" stroke="#758569" stroke-width="1.3"/>
        <g transform="rotate({swing*6} 238 158)">
          <path d="M238 157v7" stroke="#b7a470"/>
          <path d="M244 166a8 8 0 1 0 0 12a7 7 0 0 1 0-12" fill="#c5b273" stroke="#e2cc8c" stroke-width=".7"/>
        </g>
        <g transform="rotate({swing*1.6} 262 119)">
          <path d="M221 95 L209 56 Q225 57 245 79 L280 76 Q297 51 311 55 L307 97
          L318 111 309 113 321 126 309 128 315 139 301 140 298 152 287 148
          Q262 164 237 150 L225 155 224 145 210 143 216 133 205 130 214 117 205 114Z" fill="url(#fur)"/>
          <path d="M219 70l9 24 13-12Z M298 71l-11 14 15 9Z" fill="#9b8e84" stroke="#586357"/>
          <path d="M229 87l-7-8m74 5 6-9" fill="none" stroke="#b2b3a0" stroke-width="1.2"/>
          <path d="M230 120l-9 10 12 1-7 9 12-1q12 17 25 12q16 7 30-13l11-2-10-6 9-6-12-5
          Q275 123 268 117 Q249 124 230 120Z" fill="url(#ruff)" stroke="none"/>
          <path d="M259 82l5 16 5-12 5 10 5-17" fill="none" stroke="#23392d" stroke-width="4" opacity=".7"/>
          <path d="M233 103q13-9 25 2m16-1q12-10 25-6" fill="none" stroke="#c3c3a7" stroke-width="2.3" opacity=".6"/>
          {eyes}
          <ellipse cx="255" cy="135" rx="12" ry="9" fill="#a2ab98" stroke="none"/>
          <ellipse cx="277" cy="134" rx="11" ry="9" fill="#a2ab98" stroke="none"/>
          <path d="M260 130q6-3 13-1l-7 7Z" fill="#4d4540" stroke="#28392d" stroke-width="1.5"/>
          {mouth}
          <g fill="none" stroke="#c2c6ab" stroke-width="1" opacity=".8">
            <path d="M246 133l-31-6m30 10-33 3m35 1-26 10m65-20 29-8m-28 12 30 1m-30 4 24 8"/>
          </g>
          <g fill="#566451" stroke="none"><circle cx="250" cy="132" r="1"/><circle cx="253" cy="137" r="1"/><circle cx="281" cy="131" r="1"/><circle cx="279" cy="137" r="1"/></g>
          <g transform="rotate(-12 261 72)">
            <path d="M203 66q-14-4-20 3q8 20 70 23q56 5 78-10q8-5 5-11q-15 10-35 3Z" fill="#19261e" stroke="#93977f"/>
            <path d="M221 72 L225 37 Q227 26 246 31 L264 12 Q274 8 288 21 L296 75Z" fill="url(#hat)"/>
            <path d="M229 36q12 10 22 4l14-18q9-9 20-1" fill="none" stroke="#646e5b" stroke-width="2" opacity=".7"/>
            <path d="M221 60q37 17 74 2l1 12q-36 15-77-1Z" fill="#5c5b44" stroke="#777858" stroke-width="1.1"/>
            <path d="M254 67l13 2-1 12-13-2Z" fill="#212e22" stroke="#c5ae6b" stroke-width="2.2"/>
            <path d="M260 69v9" stroke="#ae995f" stroke-width="1.4"/>
            <path d="M202 74q51 20 117 6" fill="none" stroke="#66745b" stroke-width="1.2"/>
          </g>
        </g>
      </g></g></svg>'''
