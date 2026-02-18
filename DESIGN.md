# "Waar is Jeffrey?" — Design Document
## Satirisch Museum-Installatie Spel

### Concept
Een digitale "Where's Waldo"-ervaring als politiek commentaar op Jeffrey Epstein's banden met koninklijke families en machthebbers. Spelers zoeken Epstein in bewerkte historische schilderijen — hij is subtiel aanwezig, geschilderd in de stijl van het origineel.

---

## Technische Architectuur

### Image Pipeline
1. **Bronmateriaal**: Public domain schilderijen (hoge resolutie, Wikimedia/Rijksmuseum API)
2. **AI Editing**: Krea Nano Banana Pro (4K) — houdt origineel maximaal intact
3. **Prompt Strategy**: 
   - Beschrijf exacte positie (percentage x,y)
   - Specificeer de schilderstijl (chiaroscuro, impasto, etc.)
   - Benadruk subtiliteit: "barely noticeable unless carefully examined"
   - Kleding periode-correct (17e eeuws voor Nachtwacht, etc.)
4. **Coordinate Mapping**: Na generatie → visueel inspecteren → exacte hitbox coördinaten vastleggen als percentage van beeldgrootte

### Hitbox Systeem
```javascript
levels: [
  {
    id: "nachtwacht",
    image: "images/edited/nachtwacht_4k.jpg",
    originalImage: "images/originals/night_watch.jpg",  // voor vergelijking
    jeffreyX: 0.85,  // percentage van links
    jeffreyY: 0.45,  // percentage van boven  
    radius: 0.04,    // hitbox radius als percentage van beeldbreedte
    difficulty: "hard",
    timer: 60,
    title: "De Nachtwacht — Rembrandt, 1642",
    funFact: "Epstein bezocht het Rijksmuseum meerdere keren...",
    hint: "Zoek in de schaduwen rechts..."
  }
]
```

---

## UI/UX Design — Museum-Installatie Kwaliteit

### Inspiratie
- Google Arts & Culture (gigapixel zoom)
- Rijksmuseum online collectie
- "Where's Waldo?" officiële apps
- Museum touchscreen installaties

### Core Interactie: Deep Zoom
```
┌─────────────────────────────┐
│  [Schilderij - volledig]    │  ← Initieel overzicht
│                             │
│     Pinch/scroll to zoom    │
│     Drag to pan             │
│     Tap to guess            │
│                             │
└─────────────────────────────┘
         ↓ zoom in
┌─────────────────────────────┐
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░ │  ← Detail view
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░ │     Brushstrokes zichtbaar
│ ░░░░░░░👤░░░░░░░░░░░░░░░░░ │     Jeffrey ergens hier...
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░ │
└─────────────────────────────┘
```

### Features
1. **Smooth pinch-zoom** (mobile) + scroll-zoom (desktop)
   - Lib: OpenSeadragon of Panzoom
   - Deep Zoom Image tiles voor 4K+ zonder lag
   
2. **Magnifying glass mode**
   - Optioneel vergrootglas dat je over het schilderij sleept
   - Extra immersief, museum-achtig

3. **Timer met spanning**
   - Ticking clock geluid (subtiel)
   - Timer wordt rood bij <10s
   - "Hint" knop die 10s kost maar een richting geeft

4. **Reveal animatie**
   - Bij vondst: zachte gouden glow rond Jeffrey
   - Slide-in panel met:
     - Origineel vs bewerkt (slider vergelijking)
     - Fun fact over Epstein's connectie
     - "Volgende schilderij →"

5. **Score systeem**
   - Sneller vinden = meer punten
   - Geen hint gebruikt = bonus
   - Leaderboard (lokaal)

6. **Visuele stijl**
   - Donker, elegant (museum-muur gevoel: #1a1a1a achtergrond)
   - Playfair Display + serif fonts
   - Gouden accenten (#c4a35a)
   - Subtiele textuur (canvas/linnen patroon)
   - Schilderijlijst-effect rond elke afbeelding (CSS box-shadow + border)

7. **Introscherm**
   - Dramatic quote: "He was everywhere. Can you find him?"
   - Korte uitleg concept
   - "Begin de zoektocht" knop

8. **About/Disclaimer**
   - Satirisch kunstproject
   - Bronvermelding schilderijen
   - Links naar Epstein documentatie

### Mobile-First
- Touch events voor zoom/pan
- Responsive: schilderij vult scherm
- Haptic feedback bij vondst (navigator.vibrate)
- Volledig scherm modus

---

## Schilderijen Selectie (7-10 levels)

| # | Schilderij | Kunstenaar | Jaar | Koninklijk Huis | Moeilijkheid |
|---|-----------|-----------|------|----------------|-------------|
| 1 | De Oranjes (Tom's foto) | Modern | 2020s | Nederland | Makkelijk |
| 2 | De Nachtwacht | Rembrandt | 1642 | Nederland | Medium |
| 3 | Kroningsbanket George IV | G. Jones | 1821 | Groot-Brittannië | Medium |
| 4 | School van Athene | Raphael | 1511 | Vaticaan/Macht | Moeilijk |
| 5 | Boerenbruiloft | Bruegel | 1567 | Habsburgers | Moeilijk |
| 6 | Het Laatste Avondmaal | Da Vinci | 1498 | Macht/Religie | Zeer moeilijk |
| 7 | Bar at Folies-Bergère | Manet | 1882 | Frankrijk | Medium |

### Per schilderij vastleggen:
- Gewenste Epstein-positie (x%, y%)
- Beschrijving van hoe hij erin past (kleding, houding, belichting)
- Prompt voor Nano Banana Pro
- Na generatie: exacte hitbox coördinaten + radius

---

## Tech Stack
- **HTML5 + CSS3 + Vanilla JS** (geen framework nodig)
- **OpenSeadragon** of **Panzoom** voor deep zoom
- **Howler.js** voor audio (optioneel: spanning muziek)
- **4K PNG images** via Krea Nano Banana Pro
- **Python SimpleHTTPServer** voor hosting
- **Cloudflare Tunnel** voor publieke toegang
