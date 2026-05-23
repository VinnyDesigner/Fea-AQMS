import re
import sys

def convert_html_to_jsx(html_path, jsx_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Extract the dashboard-header onwards until the script tags
    match = re.search(r'(<!-- Dashboard Header -->.*?)</div>\s*</div>\s*<script', html, re.DOTALL)
    if match:
        body = match.group(1)
    else:
        print("Could not find body in HTML")
        sys.exit(1)

    # basic replacements
    body = body.replace('class=', 'className=')
    body = body.replace('stroke-width=', 'strokeWidth=')
    body = body.replace('stroke-linecap=', 'strokeLinecap=')
    body = body.replace('stroke-linejoin=', 'strokeLinejoin=')
    body = body.replace('fill-rule=', 'fillRule=')
    body = body.replace('clip-rule=', 'clipRule=')
    body = body.replace('stop-color=', 'stopColor=')
    
    # replace HTML comments with JSX comments
    body = re.sub(r'<!--(.*?)-->', r'{/* \1 */}', body)

    # replace styles
    def style_replacer(m):
        style_str = m.group(1)
        # simplistic conversion of style="key: value; key2: value;" to style={{key: 'value', key2: 'value'}}
        rules = style_str.split(';')
        jsx_rules = []
        for r in rules:
            if not r.strip(): continue
            k, v = r.split(':', 1)
            k = k.strip()
            v = v.strip().replace("'", "\\'")
            # camelCase the key
            k_parts = k.split('-')
            k_camel = k_parts[0] + ''.join(x.capitalize() for x in k_parts[1:])
            jsx_rules.append(f"{k_camel}: '{v}'")
        return 'style={{' + ', '.join(jsx_rules) + '}}'
    
    body = re.sub(r'style="([^"]*)"', style_replacer, body)
    
    # fix void tags
    body = re.sub(r'<input([^>]*[^/])>', r'<input\1 />', body)
    body = re.sub(r'<br>', r'<br/>', body)

    # Map part: replace <div id="fujairah-map"...></div> with Leaflet code
    # We will just inject the MapContainer block instead of the map div.
    map_code = """
        <MapContainer center={[25.1288, 56.3265]} zoom={12} style={{width: '100%', height: '100%', zIndex: 1, minHeight: '300px'}}>
            <TileLayer url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png" attribution='&copy; CARTO' />
            <Marker position={[25.1288, 56.3265]} icon={createCustomIcon('77', '#fcd34d')} />
            <Marker position={[25.1450, 56.3400]} icon={createCustomIcon('45', '#84cc16')} />
            <Marker position={[25.1100, 56.3300]} icon={createCustomIcon('120', '#f97316')} />
            <Marker position={[25.1350, 56.3050]} icon={createCustomIcon('45', '#84cc16')} />
            <Marker position={[25.1200, 56.3550]} icon={createCustomIcon('150', '#ef4444')} />
            <Marker position={[25.1050, 56.3450]} icon={createCustomIcon('180', '#ef4444')} />
        </MapContainer>
        <div style={{position: 'absolute', bottom: '10%', left: '5%', fontSize: '2.25rem', fontWeight: '800', color: '#111', letterSpacing: '-1px', textShadow: '0px 2px 10px rgba(255,255,255,0.8), 0px 0px 5px rgba(255,255,255,1)', zIndex: 1000, pointerEvents: 'none'}}>Fujairah</div>
"""
    body = re.sub(r'<div id="fujairah-map"([^>]+)></div>\s*<div style={{position: \'absolute\', bottom: \'10%\', left: \'5%\', fontSize: \'2.25rem\', fontWeight: \'800\', color: \'#111\', letterSpacing: \'-1px\', textShadow: \'0px 2px 10px rgba\(255,255,255,0.8\), 0px 0px 5px rgba\(255,255,255,1\)\', zIndex: \'1000\', pointerEvents: \'none\'}}>Fujairah</div>', map_code, body, flags=re.DOTALL)
    
    # Also I need to remove onclick="toggleDropdown(this)"
    body = body.replace('onclick="toggleDropdown(this)"', '')

    # A weird character 'A' was found in the text (like 24.59Ac) due to encoding issues. Replace it.
    body = body.replace('Ac', '°C')
    body = body.replace('A ', 'º ')

    final_jsx = f"""import React from 'react';
import Dropdown from '../components/Dropdown';
import {{ MapContainer, TileLayer, Marker }} from 'react-leaflet';
import L from 'leaflet';

const createCustomIcon = (value, color) => {{
  const textColor = (color === '#fcd34d') ? '#854d0e' : 'white';
  return L.divIcon({{
    className: 'custom-map-marker',
    html: `<div style="width: 24px; height: 24px; background: ${{color}}; color: ${{textColor}}; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.6rem; font-weight: bold; border: 2px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">${{value}}</div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12]
  }});
}};

const LiveData = () => {{
  return (
    <>
{body}
    </>
  );
}};

export default LiveData;
"""
    with open(jsx_path, 'w', encoding='utf-8') as f:
        f.write(final_jsx)
    print("Successfully converted.")

if __name__ == "__main__":
    convert_html_to_jsx("legacy/live-data-raw.txt", "src/pages/LiveData.jsx")
