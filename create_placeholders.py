# Create SVG images for placeholders
waste1_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
  <rect width="600" height="400" fill="#f87171" rx="12"/>
  <rect x="20" y="20" width="560" height="360" fill="#fee2e2" rx="8" stroke="#dc2626" stroke-width="3" stroke-dasharray="8 8"/>
  <circle cx="300" cy="160" r="60" fill="#fca5a5"/>
  <path d="M280 140 L320 180 M320 140 L280 180" stroke="#991b1b" stroke-width="8" stroke-linecap="round"/>
  <path d="M260 210 Q300 240 340 210" stroke="#991b1b" stroke-width="6" fill="none" stroke-linecap="round"/>
  <text x="300" y="270" font-family="Arial, sans-serif" font-size="22" font-weight="bold" fill="#991b1b" text-anchor="middle">Reported Waste Site</text>
  <text x="300" y="300" font-family="Arial, sans-serif" font-size="14" fill="#b91c1c" text-anchor="middle">Garbage Accumulation &amp; Debris</text>
</svg>'''

waste2_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
  <rect width="600" height="400" fill="#fb923c" rx="12"/>
  <rect x="20" y="20" width="560" height="360" fill="#ffedd5" rx="8" stroke="#ea580c" stroke-width="3" stroke-dasharray="8 8"/>
  <circle cx="300" cy="160" r="60" fill="#fdba74"/>
  <text x="300" y="175" font-family="Arial, sans-serif" font-size="48" text-anchor="middle">&#9888;</text>
  <text x="300" y="270" font-family="Arial, sans-serif" font-size="22" font-weight="bold" fill="#9a3412" text-anchor="middle">Litter &amp; Overflowing Bins</text>
  <text x="300" y="300" font-family="Arial, sans-serif" font-size="14" fill="#c2410c" text-anchor="middle">Municipal Attention Needed</text>
</svg>'''

resolved_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
  <rect width="600" height="400" fill="#34d399" rx="12"/>
  <rect x="20" y="20" width="560" height="360" fill="#d1fae5" rx="8" stroke="#059669" stroke-width="3"/>
  <circle cx="300" cy="160" r="60" fill="#6ee7b7"/>
  <path d="M275 160 L293 178 L328 142" stroke="#065f46" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="300" y="270" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#065f46" text-anchor="middle">Task Completed &amp; Area Cleaned</text>
  <text x="300" y="300" font-family="Arial, sans-serif" font-size="14" fill="#047857" text-anchor="middle">Verified by Waste Collector</text>
</svg>'''

with open('static/images/waste_sample1.svg', 'w') as f:
    f.write(waste1_svg)
with open('static/images/waste_sample2.svg', 'w') as f:
    f.write(waste2_svg)
with open('static/images/resolved_sample.svg', 'w') as f:
    f.write(resolved_svg)

# Also write jpg names as alias or copies
with open('static/images/waste_sample1.jpg', 'w') as f:
    f.write(waste1_svg)
with open('static/images/waste_sample2.jpg', 'w') as f:
    f.write(waste2_svg)
with open('static/images/resolved_sample.jpg', 'w') as f:
    f.write(resolved_svg)

print("Placeholder graphics created successfully.")
