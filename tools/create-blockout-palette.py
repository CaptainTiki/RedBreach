"""Create additive Kenney palette copies; original pixels and map assignments stay intact."""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
TEXTURES = ROOT / 'RedBreach/textures/greybox'
PATTERNS = ('01', '03', '06')
VARIANTS = {
    'GreyCharcoal': ('Dark', 28),
    'GreyMedium': ('Dark', 96),
    'GreyPale': ('Dark', 150),
    'MutedGreen': ('Green', None),
    'MutedOrange': ('Orange', None),
    'MutedRed': ('Red', None),
    'MutedPurple': ('Purple', None),
    'DarkGreen': ('Green', None),
    'DarkOrange': ('Orange', None),
    'DarkRed': ('Red', None),
    'DarkPurple': ('Purple', None),
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    originals = {p: digest(p) for c in ('Dark', 'Light', 'Green', 'Orange', 'Red', 'Purple') for p in (TEXTURES/c).glob('*.png')}
    manifest = []
    for name, (source, grey) in VARIANTS.items():
        folder = TEXTURES/name
        folder.mkdir(exist_ok=True)
        for pattern in PATTERNS:
            src = TEXTURES/source/f'texture_{pattern}.png'
            dst = folder/src.name
            image = Image.open(src).convert('RGBA')
            rgb = image.convert('RGB')
            if grey is not None:
                # Anchor the Dark sheet's background luminance (51) to this grey.
                # Preserve light grid/text contrast; identical monotonic mapping at every pixel.
                lut = [max(0, min(255, round(grey+(v-51)*(235-grey)/204))) for v in range(256)]
                result = rgb.convert('L').point(lut).convert('RGB')
            else:
                brightness = 0.50 if name.startswith('Dark') else 0.80
                result = ImageEnhance.Brightness(ImageEnhance.Color(rgb).enhance(0.28)).enhance(brightness)
            result.putalpha(image.getchannel('A'))
            result.save(dst)
            assert Image.open(dst).size == image.size == (1024, 1024)
            assert Image.open(dst).getchannel('A').tobytes() == image.getchannel('A').tobytes()
            # Let Godot generate unique UIDs/cache paths, keeping the source import parameters.
            imp = Path(str(dst)+'.import')
            if not imp.exists():
                params = Path(str(src)+'.import').read_text().split('[params]', 1)[1]
                params = params.replace('mipmaps/generate=false', 'mipmaps/generate=true')
                imp.write_text('[remap]\nimporter="texture"\ntype="CompressedTexture2D"\n\n[params]'+params)
            manifest.append({'file': str(dst.relative_to(ROOT)).replace('\\','/'), 'source': str(src.relative_to(ROOT)).replace('\\','/'), 'source_sha256': originals[src], 'sha256': digest(dst)})
    assert all(digest(p) == h for p, h in originals.items())
    (ROOT/'docs/blockout-palette.json').write_text(json.dumps({'patterns':list(PATTERNS),'colour_saturation':0.28,'colour_brightness':0.80,'dark_colour_brightness':0.50,'grey_backgrounds':{'GreyCharcoal':28,'Dark_existing':51,'GreyMedium':96,'GreyPale':150},'files':manifest}, indent=2)+'\n')
    preview = Image.new('RGB',(1328,1320),'#171a1e')
    draw = ImageDraw.Draw(preview)
    fontpath = 'C:/Windows/Fonts/segoeui.ttf'
    font = ImageFont.truetype(fontpath,22)
    small = ImageFont.truetype(fontpath,17)
    title = ImageFont.truetype(fontpath,30)
    draw.text((24,18),'RED BREACH  /  Blockout palette',font=title,fill='white')
    draw.text((24,62),'Exact colour variants - original grid artwork and 1 metre repeats preserved',font=small,fill='#bfc5cd')
    names = ['GreyCharcoal','Dark','GreyMedium','GreyPale','MutedGreen','MutedOrange','MutedRed','MutedPurple','DarkGreen','DarkOrange','DarkRed','DarkPurple']
    for i, name in enumerate(names):
        x,y = 24+(i%4)*326, 110+(i//4)*396
        label = 'Dark (existing)' if name=='Dark' else name
        draw.text((x,y),label,font=font,fill='white')
        tile=Image.open(TEXTURES/name/'texture_01.png').convert('RGB').resize((300,300),Image.Resampling.LANCZOS)
        preview.paste(tile,(x,y+38))
        if name.startswith('Muted') or name in ('DarkGreen', 'DarkOrange', 'DarkRed', 'DarkPurple'):
            source=VARIANTS[name][0]
            original=Image.open(TEXTURES/source/'texture_01.png').convert('RGB').resize((46,46),Image.Resampling.LANCZOS)
            preview.paste(original,(x,y+346))
            draw.text((x+55,y+355),'Original colour',font=small,fill='#bfc5cd')
        else:
            draw.text((x,y+350),'Grid / panel / floor-cross patterns',font=small,fill='#bfc5cd')
    preview.save(ROOT/'docs/blockout-palette.png')
    print(f'Created {len(manifest)} textures. Verified dimensions, alpha and {len(originals)} unchanged source PNGs.')

if __name__ == '__main__':
    main()
