# Enclosure (shell) design

Started 2026-11-09. This file holds the shell discussion: decisions, open questions and notes. Dimensions from the
boards and parts are in `mechanical_inputs.md` beside it. The electronics and the JLCPCB order are tracked separately
in `docs/board_status.md`.

Shell decisions are numbered **E1, E2, ...** so they don't mix with the board decisions (D1-D117 in
`docs/DECISIONS.md`).

## Fixed by the boards

Both boards are in production (2026-11-19), and the user decided on 2026-11-20 not to change them. The shell fits
the boards as they are:

- Board A 95 x 65 x 1.2 mm with its edge connectors where they are: USB-A x 2 at the device top, USB-C and the
  camera cables on the right, SIM, microSD and the three buttons on the left, battery and keyboard cable toward
  the keyboard.
- Board B 74 x 53.1 x 2.0 mm, the BBQ20KBD outline, under the Q20 keyboard.
- Component stack 10.65 mm on Board A (9.35 without the battery connector).

## Assumed so far, open to change without touching the boards

These come from checkpoints 1-3 and were never designed as a shell:

- Layout: display above the keyboard on the front; Board A behind the display, battery behind the keyboard, both
  in one shell, about 95 x 150 x 15 mm (rough estimate).
- Display FPC toward the device's left side (the board's J701 position requires the tail to come over the board's
  right edge).
- CM5 cooled by a heat spreader to the display frame.
- Cameras placed by the shell, on 150 mm cables from the device's right side.
- Board-to-board FFC about 50 mm.

## Open questions

1. ~~Overall form~~: decided 2026-11-19, a half-apple slab of about 120 x 180 x 20 mm (E7), replacing the
   FLIPOUT-style swivel (E1, E3-E5). Fit check in the notes below.
2. **Screen size:** the 4.0" panel's module is 84 mm wide and the board makes the device about 98 mm wide anyway, so
   there are about 11 mm of width a bigger panel could use without widening the device. A different panel means a
   board change (J701, display routing) before the re-order.
3. ~~How it's made~~: decided, 3D printing (E6). Still open: the home printer type and the service and material for
   the final shell.
4. **Opening and service:** how the back comes off; battery access; reaching the debug pads, the RESET / MASKROM /
   RECOVERY buttons (under the display), SIM and microSD.
5. **Display mounting:** frame, adhesive or bezel; how the FPC tails fold behind the panel.
6. **Keyboard mounting:** how the Q20 keyboard and Board B are held; the BBQ20KBD reference has its own approach.
7. **Thermal:** CM5 heat path (spreader to the display frame, or to the back / a metal part), LTE modem thermal pad.
   Since E11 the rear camera's 32 x 32 board covers about 18 x 31 mm of the modem's outline (socket and card,
   31 x 42), 0.3 mm from it: a pad from the modem to the back plate has the rest, and the camera takes some of the
   modem's heat.
8. **Antennas:** Wi-Fi x 2 and LTE x 2-3; where they sit, non-metal windows, spacing from the battery and the boards.
9. **Cameras:** positions decided (E11, E12, replacing those of E9 and E10). Still open: a front camera module
   whose lens head fits 7.5 mm tall and 5.4 mm deep between the screen and the keys (E12); the lens windows; the
   cables' routes and spare length.
10. **Buttons and lights:** plungers through the skin for the three side switches, 10-12 mm long (assumed, not
    decided). The board's two LEDs (D302, D501, under the display's left edge): a light pipe of about 18 mm to the
    skin's left side, or left hidden.
11. **Speakers and microphone:** speaker size, acoustic chambers and grilles. The board's microphone listens through
    a 0.5 mm hole to the back face of Board A (near the device's left side, about 17 mm below the board's USB-A edge).
    The back shell needs a sealed sound path there.
12. **Ports:** decided with E8. Still open: the USB-C socket holder, to be designed once the extension cable is
    bought and measured; the lid design.

## Decisions

| # | Decision | Reason |
|---|---|---|
| E1 | *Superseded by E7 (2026-11-19).* **Form: a swivel like the Motorola FLIPOUT.** Two halves of the same size. The screen half turns 90 degrees about a pivot near one corner to uncover the keyboard below the screen. (2026-11-09) | The user's choice. The square 720 x 720 panel loses nothing when the picture rotates 90 degrees. |
| E2 | *Still applies; its thickness is superseded by E7.* **Internals unchanged, including the 85 x 65 x 8 mm 5000 mAh battery under Board B in the keyboard half; closed thickness about 34 mm accepted** ("3 cm feels appropriate"). (2026-11-09) | The user's choice: keep the boards and the battery as they are. Thinner options (5 mm or a narrow cell beside Board B, 27-31 mm) were set aside for now. |
| E3 | *Superseded by E7 (2026-11-19).* **Rear camera in the screen half, on its back: usable only with the device open.** (2026-11-09) | The user's choice: having to swivel the device open before taking a photo feels tactile. When closed the lens faces into the keyboard half and is protected. |
| E4 | *Superseded by E7 (2026-11-19).* **Keyboard half about 3 mm thicker (about 20.5 mm); closed thickness about 37 mm** (replaces the 34 mm of E2). (2026-11-09) | The user's choice of fix (a). The camera's closed position overlaps the battery's top edge by 3 mm in plan, and the channel needs 10.8 mm of depth there. With 20.5 mm the channel floor ends 9.7 mm above the back face, 0.5 mm above the battery (9.2). |
| E5 | *Superseded by E7 (2026-11-19).* **Pivot on the right (seen from the front), set in 22.5 mm from both edges; rear camera at the screen half's top-right, behind Board A next to J704; when closed it sits in a curved channel in the keyboard half's top-left corner.** (2026-11-09) | Recommended with the camera study and accepted with E4 ("yeah"). On the left, the camera would sit over the charger's power stage and the microphone port. Cost: battery harness about 120-150 mm (24 AWG keeps the 25 mV budget to 120 mm) and a longer FFC. |
| E6 | **Made by 3D printing:** mock-ups and test prints at home first, the final shell from a printing service. (2026-11-09) | The user's plan. Design rules for both: walls of at least 1.6 mm (four 0.4 mm FDM perimeters), 0.3-0.5 mm clearance on moving fits, heat-set brass inserts for screws, and a metal pivot rather than a printed one. Check the service's own rules once it is chosen. |
| E7 | **Form: a half-apple slab, about 120 x 180 x 20 mm** (`img/half_apple_sketch.png`, drawn to scale). The front is the cut face with the display above the keyboard; the green skin forms the rim and the rounded back; stem and leaf on top. Board A behind the display; the battery (85 x 65 x 8, E2) stands upright behind the display's lower edge and the keyboard. **Replaces E1 and with it E3-E5.** (2026-11-19) | The user's design. Fits in plan and in 20 mm (notes, 2026-11-19); no pivot, short battery harness and keyboard FFC, room in the skin for antennas and speakers. |
| E8 | **Ports in the apple's skin:** USB-A x 2 behind openings with **rubber lids**, the openings large enough for the plug bodies (the receptacle mouths are about 8.6 mm behind the outer surface); **USB-C through a store-bought extension cable** from J101 to a socket held in the skin; **SIM and microSD reached with the back plate off** (planned that way from the start). (2026-11-19) | The user's choices. The extension: a sideways 90-degree plug into J101 (about 10 mm from the board edge to the inside of a 2 mm wall) and a socket end under about 20 mm long, placed on the right just below Board A, beside the battery (21-24 mm of room there). J101 carries only USB 2.0, CC and VBUS, so any USB 2.0 extension rated for 3 A works. |
| E9 | *Position superseded by E11 (2026-11-21).* **Rear camera (Radxa 13M 214) in the middle of the back plate, in a bump.** (2026-11-19) | The user's choice. At the exact centre of the back (x' 47.5, y' about 78) the camera sits over the battery's top end: front stack to the battery's back about 16.3 + camera 10.8 (0.3 gap, parts 1.5, board 1.6, lens 6.38, window 1.0) = about 27.1, so the bump stands **about 7 mm** proud of the 20 mm back. On the same centre line about 3 cm higher, behind Board A over the LTE modem: 11.06 + 3.55 + 10.8 = about 25.4, a bump of **about 5.4 mm**, but the sensor then sits on the modem's heat. The battery stays 85 x 65 x 8 either way. The 31P connector is on the lens side, so the cable folds round the camera board's edge inside the bump. |
| E10 | *Superseded by E12 (2026-11-21).* **Front camera at the top centre, right above the screen.** (2026-11-19) | The user's choice. **The Radxa 8M 219 does not fit there:** its board is 32 x 32 mm with the lens in the middle and 16 mm deep (Radxa brief). Above the display there are only 7.7 mm (under the stem notch, inside a 2 mm wall) to 12.8 mm (under the lobes) before the skin, and behind the display's top edge Board A and the CM5 leave about 1.5 mm. Placing that module above Board A would put its lens about 19 mm above the screen and the apple about 27 mm taller. The 13M 214 (the rear camera) has the same 32 x 32 mm board with the lens in the middle; it is shallower (9.5 mm), but the board's area is the problem, so it does not fit there either: above the screen its board would stand 5-10 mm out of the apple's top, and below its lens, behind the screen, it would hit the CM5 and USB-A J401. **So the spot needs a smaller front camera**: the same IMX219 sensor on a small head (Radxa lists the Raspberry Pi Camera V2 as compatible with the same 15-pin connector), lens head under about 7.5 mm tall and under about 5 mm deep in front of the CM5. A specific module with a drawing is still to be found. |
| E11 | **Rear camera high on the back's centre line: centre at x' 47.5, y' 26.5, in a bump 5.4 mm proud.** (2026-11-21) | The user's choice, after printing v1: higher, so it doesn't get in the way of the grip. y' 26.5 is the highest spot where the 40 x 40 bump and its R 2 blend stay on the flat back (3.4 mm inside the R 10 back edge); its top edge is 13.4 mm below the stem notch, its bottom edge at y' 46.5. Anywhere behind Board A on the centre line the camera sits over the LTE modem (socket J501 and the card, 3.55 mm), so the bump is 5.39 mm anywhere from y' 18 to 64 (7.04 over the battery in v1). The board covers about 18 x 31 mm of the modem's outline (Q7). The cable to J704 (y' 18.5, device right) is now short, so the 150 mm cable has to be folded up. With nothing behind the battery any more, it moved back to Z 3.5-11.5, as far as the R 10 back edge allows. |
| E12 | **Front camera centred between the screen and the keyboard: lens at x' 47.5, y' 91.1.** (2026-11-21) | The user's choice, replacing E10's spot above the screen. The visible band from the display's bottom edge (y' 87.06) to the keyboard's top edge (y' 100.9) is 13.8 mm, but under it the display and Board B's top edge (y' 95.2) leave a slot **7.5 mm** tall for the lens head (0.3 mm clearance each side), so the lens sits 4 mm below the screen and 10 mm above the keys. The keyboard FFC (J1001 to J101, both on the centre line) runs behind it, so on the centre line the head can be **5.4 mm** deep (to a 1 mm window in the 2 mm front wall); with the lens centre 7.3 mm or more to one side of the cable, 7.2 mm. The camera's flex can leave sideways, or upward behind the display in the space in front of the battery (Z 11.8-15.9, about 4.1 mm), and go on to J705 (y' 35, device right). **No module is chosen:** needed is an IMX219 head (15-pin Pi-camera type, for Radxa's 31P-to-15P cable) within 7.5 x 5.4 mm. For scale, the 13M 214's lens block is 8.5 x 8.5 x 6.38 mm (Radxa brief). If the module needs more height, the display can move up, since the band above it no longer holds a camera: 1.6 mm up gives a 9.1 mm slot and leaves the screen 7.4 mm from the outline (the keyboard is 7.6). |

## Notes

### 2026-11-21: cameras moved, block model v2 (asked for by the user after printing v1)

The user printed v1 and liked it, then moved both cameras: the rear one higher, out of the grip (E11), and the
front one between the screen and the keyboard (E12). Everything else is as in v1.

**Files**
- `model/apple_v2.step`: as v1, plus the keyboard FFC and the front camera's space (a red box: the room for the
  lens head, not a module).
- `model/apple_v2_mockup.stl`: for printing.
- `img/apple_v2_view_*.png`: the same views as v1, plus `inside_front`: from the front with the shell, display
  and keyboard left out, showing the camera space over the FFC.
- Rebuild as for v1 (`tools/enclosure_apple.py OUT_DIR`). The script now writes v2 names; the v1 files stay
  beside them.

**What changed**
- **Rear camera (E11):** centre at x' 47.5, y' 26.5, behind Board A over the LTE modem.
  - The bump is the same 40 x 40, R 8 corners, but **5.4 mm** proud instead of 7.0.
  - Its top edge is 13.4 mm below the stem notch, its bottom edge at y' 46.5. That leaves about 121 mm of plain
    back below it, from y' 46.5 to the bottom.
- **Battery:** moved back to Z 3.5-11.5 (v1 3.74-11.74). It now touches neither the camera's cable nor anything
  else behind it. It can't go further back: at Z 3.5 its bottom corner meets the curve of the R 10 back edge.
- **Keyboard FFC modelled,** 12P 0.5 mm, 6.5 x 0.3 mm (typical values, UNVERIFIED; no cable chosen).
  - The path: from J1001's mouth (y' 64.7, Z 11.14), over the battery's top front edge (y' 66.9, Z 11.95), then
    straight to J101's mouth (y' 95.5, Z 13.2).
  - **30.9 mm between the connector mouths,** plus the insertion depth at each end (not dimensioned). This is the
    length to order the cable by (mechanical_inputs.md; the checkpoint 3 estimate was about 50).
  - Both connectors' slot heights are taken at half the body height (UNVERIFIED).
- **Front camera (E12):**
  - A 4 mm lens mark at x' 47.5, y' 91.1, between the screen and the keys. The mark above the screen is gone.
  - Behind the mark, the space for the lens head: 7.5 mm square, Z 13.6-19.0 (5.4 mm deep), in front of the FFC.

**Checks (all by the script)**
- 0 sharp convex edges.
- No part in the 2 mm walls.
- No overlaps:
  - rear camera with Board A or the battery;
  - FFC with the battery, display or either board;
  - the front camera's space with the FFC, battery, display or either board.
- Unchanged from v1:
  - display 8.5 mm and keyboard 7.6 mm from the outside edge;
  - display back 0.2 mm over J102.
- STL closed: every edge used twice, Euler characteristic 2.

**Printing**
About **120.5 x 195.2 x 25.4 mm** on the bed, front face down, no supports, as for v1. It is 1.6 mm lower than v1
because the bump is lower.

### 2026-11-20: half-apple block model v1 and printable mock-up (asked for by the user: "no sharp edges")

*The camera positions and the battery depth here are superseded by v2 (2026-11-21, above); the rest still applies.*

**Files**
- `model/apple_v1.step`: the shell, with Board A and Board B (part envelopes), the battery, display, keyboard
  placeholder and rear camera inside. Opens in FreeCAD, Fusion or Onshape.
- `model/apple_v1_mockup.stl`: for printing.
- `img/apple_v1_view_*.png`: pictures (front, back, side, top, three-quarter views, and the inside).
- `model/apple_outline.json`: the outline traced from the sketch, made symmetric and rounded
  (`tools/apple_outline.py`).

**To rebuild**
1. Re-export the board envelopes when the boards change:
   `python3 tools/board_envelopes.py hw/board_a/cm5_carrier.kicad_pcb docs/enclosure/model/board_a_envelope.json`,
   and the same for board_b. Done again on 2026-11-20: since the swivel model, only J702, SW304 and TP305 had moved.
2. Trace the outline: `tools/apple_outline.py`.
3. Build the model: `tools/enclosure_apple.py OUT_DIR`.

Steps 2 and 3 need build123d, shapely, numpy and pillow, in a venv (`pip install --only-binary=:all: build123d
shapely numpy pillow` works on Python 3.14). All parameters are at the top of the script.

**Shape**
- **Outline:** your sketch, traced at 8.0 px/mm against Board A's dashed outline.
  - The sketch was symmetric to 0.2 mm and centred on Board A; the model makes it exactly symmetric.
  - Convex curves have a radius of at least 12 mm, the stem notch and the bottom dimple 5 mm.
  - Size: **120.4 x 180.3 mm**, without the stem and leaf.
- **Thickness 20 mm.** The front is flat with an R 2.5 edge; the back edge is R 10, as in the side view.
- **Stem and leaf:**
  - Flush with the front face: an apple cut in half through its stem shows the stem on the cut face.
  - Stem 4 mm wide (3 in the sketch, widened for strength) and 4.5 mm deep. Leaf 3.5 mm deep, tips R 2.
  - All their edges are rounded too.
- **Rear camera bump (E9):** at the exact middle of the back (x' 47.5, y' 77.6), over the battery's top end.
  - **7.0 mm** proud of the back; 40 x 40 mm, corners R 8, edge R 3, blended into the back with R 2.
  - A 10 mm lens recess.
- **Marks (rims rounded):**
  - display: 85.99 x 84 (the real orientation, tails toward the device's left), recess 0.6 mm;
  - keyboard: 70 x 40, as measured by the user, placed 5.7 mm below Board B's top edge as in the BBQ20KBD
    reference; recess 0.6 mm;
  - front camera: position only, 4 mm (E10, no module yet);
  - microphone port on the back;
  - USB-A x 2: pockets 16 x 8.5 mm (plug-body size UNVERIFIED) down to the receptacle mouths (E8);
  - USB-C: placeholder slot on the right at y' 76 (E8);
  - three button slots on the left.

**Checks (all by the script)**
- **No sharp edges:** 0 convex edges where the surface turns by more than 10 degrees. The smallest rounds:
  - the VOL- button mark, R 0.17 (the rounder could not make more there);
  - the recess rims, R 0.5;
  - the USB-A pockets, R 1.0.

  The 84 remaining non-smooth edges are inside corners (recess floors, where the stem meets the body), which are not
  sharp to the touch.
- **No part reaches into a 2.0 mm wall,** counting the R 10 back edge.
- **Room around the front parts:** the display sits 8.5 mm from the outside edge at its closest, the keyboard
  7.6 mm.
- **No overlaps:**
  - display with Board A;
  - battery with either board;
  - camera with the battery or Board A;
  - keyboard with Board B.
- **Tight spots, as before:**
  - the display's back clears the tallest Board A part (J102, 5.9 mm) by **0.2 mm**, and the CM5 height is still
    UNVERIFIED;
  - the front-camera band above the screen is 7.9 mm.
- **Battery:** Z 3.74-11.74, pushed forward against Board B to keep the bump low. That leaves 1.7 mm behind it
  for the rear camera's cable.

**What it is not**
- A solid block: no walls, split line, back plate, bosses, display or keyboard openings yet.
- The keyboard is 3 mm thick (the user measured about 2.5). The gap under it is NOT KNOWN: the model puts the
  keyboard at J201's 0.8 mm stack height, so the key tops are 3.8 mm above Board B; the reference uses 3 mm of
  foam tape.
  - With the tape, the keyboard area is 0.5 mm too deep for 20 mm. The keys would then stand 0.5 mm proud, or
    the body be 20.5 mm.
  - The camera bump would grow from 7.0 to about 8.7 mm, since the battery behind the keyboard moves back.
  - As modelled, there is 1.7 mm to spare behind the battery.
- No speakers or antennas; no front camera module.
- The USB-C and USB-A openings await the cable and the lid design.

**Printing the mock-up**
- About **120.5 x 195.2 x 27 mm** on the bed, front face down.
- No supports: the stem and leaf lie flat on the bed, the USB-A pocket ceilings bridge 16 mm, and the bump faces up.
- It needs a bed of at least about 200 mm in one direction.
- 0.2 mm layers, 3 walls, 10-15 % infill. It is a 362 cm3 block, so about 130 g of PLA at 15 % (estimate).

### 2026-11-19: half-apple slab (proposed by the user; adopted as E7, ports as E8)

The user's sketch: `img/half_apple_sketch.png`. A slab shaped like an apple cut in half: the front is the cut face,
the green skin is the rim, and the stem and leaf sit on top. The sketch also shows two orange LED "seeds" between the
display and the keyboard: a passing idea, not part of the design (the user, 2026-11-19). The back is rounded (about R 10 at the top and bottom in the side view). Board A is behind the display, and
the battery stands upright (65 wide, 85 tall) behind the display's lower edge and the keyboard. About 120 x 180 x 20 mm.
No pivot, so E1 and E3-E5 go. E2 (internals unchanged) and E6 (3D printing) still apply.

**The sketch is to scale.** Measured from the image, using Board A's dashed outline (95.0 mm = 760.5 px, 8.0 px/mm):

- **Outlines:** display 84 x 86, keyboard 74 x 53, battery 65 wide. Body 120.3 x 180.1 mm without the stem and leaf;
  skin drawn 4.7 mm thick.
- **Positions:** y' from Board A's device-top edge, x' from its left edge seen from the front.
  - Battery: x' 15-80, y' 66.9-151.9, so 1.9 mm below Board A.
  - Display bottom edge: y' 88.8. Keyboard: y' 95.2-148.

**What fits:**
- **In plan, everything.** The tight spots:
  - Board A's top corners touch the inside of the drawn skin. With a 1.6-2 mm wall instead of 4.7 there are about
    3 mm.
  - The battery's bottom corners are 2.4 mm from the skin's inside at the sides and 3.3 mm below.
  - The drawn keyboard box's bottom corners overlap the skin by 0.5 mm. Board B's bottom corners are R 14, so the
    board itself is clear, but the Q20 keyboard's own outline is still not measured.
- **Thickness 20 mm:**
  - Display zone: display 3.76 + CM5 and spreader 6.1 + board 1.2 + bottom parts 3.55 + wall 1.6 = **about 16.2**.
  - Keyboard zone: keyboard 3 (UNVERIFIED) + Board B 4.96 + battery 8 + wall 1.6 = **about 17.6**.
  - The CM5 height is still UNVERIFIED.
- **Cables get simpler than in the swivel.**
  - J102 (x' 19-41, at y' 65) sits right above the battery's top edge (y' 66.9), so the harness is a few centimetres.
  - The keyboard FFC runs straight from J1001 (x' 48) to Board B's J101: 36.4 mm, within the ~50 mm FFC planned,
    over the battery's front face.
- **Room that the swivel didn't have:**
  - The skin is 9-13 mm wider than Board A and the battery at most heights. That room can take the Wi-Fi and LTE
    antennas (top lobes and sides, away from the hands, which hold the lower half) and the speakers (beside the
    battery: 13 mm of clearance on each side at y' 122, more with a thinner wall).

**What doesn't fit as drawn:**
1. **The edge ports are buried.** The apple is about 120 mm wide where Board A is 95, so its edge features sit well
   inside the outer surface (measured to the outside of the drawn skin):

   | Feature | Board edge to outer surface | Behind the connector's front |
   |---|---|---|
   | USB-A x 2 (top, in the left lobe) | 11.6-11.7 | 8.6 (mouths 3.0 past the edge) |
   | USB-C (right) | 12.1 | 11.6 |
   | microSD / SIM (left) | 12.7 / 12.3 | about 12 |
   | VOL-, VOL+, POWER (left) | 9.7 / 11.4 / 12.3 | |

   Decided the same day as E8: rubber lids on the USB-A openings, a store-bought USB-C extension, SIM and microSD
   with the back plate off. My first suggestions were:
   - **Buttons:** plungers through the skin. Easy.
   - **SIM and microSD:** reached with the back off.
   - **USB-C:** a short extension to a receptacle in the skin. J101 carries only USB 2.0, CC and VBUS (no
     SuperSpeed lines), so a simple pigtail rated for 3 A works.
   - **USB-A:** pockets in the lobe for the plug bodies, or a local flat in the outline.
2. ~~The LED seeds are far from the board's LEDs~~: dropped, the seeds are not part of the design.
3. **The rear camera has no place within 20 mm.** No free area of 32 x 32 mm is left:
   - 8.9 mm between Board A and the skin;
   - 13 mm beside the battery;
   - 6 mm above Board A.

   Behind Board A, where E3 put it, the stack is 11.06 (front to Board A's bottom face) + 2.96 (bottom parts at the
   J704 corner) + 0.3 + 1.5 + 1.6 + 6.38 + 1.0 (window) = about **24.8 mm**, a bump of about 5 mm. The options:
   - (a) accept the bump;
   - (b) a shorter battery (about 65 x 52, roughly 3000 mAh by volume) so the camera sits behind the display's lower
     edge;
   - (c) a body about 25 mm thick.

**Size for feel:** about the footprint of a Kindle Paperwhite (about 174 x 125 mm), about 2.5 times as thick. Held in
both hands at the narrowing lower half. The battery sits low, in the palms while typing. The device is 109 mm wide at
the keyboard's top row and 81 mm at its bottom.

### 2026-11-09: Motorola FLIPOUT-style swivel (proposed by the user; adopted as E1 / E2)

The FLIPOUT (2010) is a 67 x 67 x 17 mm square phone, 120 g, 1170 mAh (Wikipedia, GSMArena, Smartprix). Its screen
half swivels 90 degrees about a corner to uncover a QWERTY keyboard below the screen.

- **Fits well:** the 720 x 720 panel is square, so the picture rotates with no loss when the screen half turns
  90 degrees. The open device puts the display above the keyboard, as the slab layout does.
- **Size of each half:** about 98 x 90 mm, set by Board A (95 mm) and the display module (84 x 86).
- **Thickness, rough:**
  - Screen half: display 3.76 + 6.1 to the board (CM5 4.6 UNVERIFIED + spreader) + board 1.2 + 3.55 underneath
    + back wall about 1.2 = about **16 mm**.
  - Keyboard half: keyboard (height not measured, about 3 assumed) + Board B 4.96 + battery 8 + back wall about
    1.2 = about **17 mm**.
  - Closed: about **33 mm**, roughly twice the FLIPOUT and twice a slab built from the same parts (about 16-17).
    A 5 mm battery of the same outline saves 3 mm, at roughly 3000 mAh instead of 5000 (estimate).
- **Closed thickness by battery option** (estimate; capacities scaled by volume from 5000 mAh for 85 x 65 x 8):

  | Battery | Where | Keyboard half | Closed |
  |---|---|---|---|
  | 85 x 65 x 8 (5000 mAh) | under Board B | about 17.5 | **about 34 mm** |
  | 85 x 65 x 5 (about 3000 mAh) | under Board B | about 14.5 | about 31 mm |
  | 85 x 33 x 8 (about 2500 mAh) | beside Board B, in the 37 mm of the keyboard half the screen half covers when open | about 10-11 | about 27-28 mm |

  Screen half about 16, gap about 0.5. The keyboard's own height (3 mm assumed) and the CM5 height are not
  measured. A smaller cell must still deliver the board's worst case (9.8 A, about 4C for 2500 mAh) or the load must
  be limited.
- **The battery cannot go in the screen half:** Board A (65 mm) + battery (65 mm) is longer than the half.
- **Through the pivot:**
  - the 12P board-to-board FFC, as a loop or spiral;
  - the battery harness: 9 x 24 AWG wires, up to about 10 A worst case.
  - A 90-degree swing with a slack loop and fine-stranded silicone wire is mild, but fatigue and strain relief need
    care.
- **Rear camera:** when closed, the back of the screen half is covered. So the camera goes either in the keyboard
  half, with its FPC through the pivot, or on the screen half, where it works only when open. The rear module is
  32 x 32 x 9.5 mm: no 32 mm strip is left beside the battery (90 - 65 = 25) or beside Board A (86 - 65 = 21)
  unless a half grows.
- **Front camera:** the display leaves about 2 mm above / below it in a 90 mm half; the module size is not known
  yet.
- **Geometry of a corner swivel** (worked out 2026-11-09):
  - **The halves must be square** for their outlines to line up both closed and open, because the screen half is
    turned 90 degrees between the two states. Board A's 95 mm gives about **98 x 98 mm**. In the screen half that
    leaves about 12 mm beyond the 86 mm display in one direction (a candidate place for the front camera, whose
    size is not known yet).
  - A pivot set in by a from both edges makes the open halves overlap by 2a. With 98 mm halves and the keyboard's
    53 mm left uncovered, 2a = 45, so a is about 22.5 mm.
  - Open, Board A's cable edge (J102, J1001) faces the keyboard. Both connectors sit left of the device centre seen
    from the front (x' 19-48), so a pivot on the left would keep the battery harness and the FFC shortest. The
    camera (below) argues for the right instead.
- **Hinge:** a metal pivot (shaft, washers, detents at 0 and 90 degrees) set into the printed or machined halves;
  the screen half (display, Board A, CM5, modem) is the heavy one.

### 2026-11-09: rear camera in the screen half (E3), consequences worked out

Front-view coordinates, open, typing orientation: keyboard half x 0-98.5, y 0-98.5 (y down); pivot set in by
a = 22.5; the screen half open covers y -53.5 to 45.

- **Only the top band of the screen half is uncovered when open.** The halves overlap by 45 mm, so only the top
  53 mm of the screen half's back is free when open, and Board A fills that band across its full width. The camera
  must therefore sit **behind Board A**.
- **That makes a bump on the screen half's back of about 8-9 mm**, about 34 x 34 mm. The stack from the outside is
  a window of about 1 + lens 6.38 + camera PCB 1.6 + its parts 1.5 + 0.3 clearance + Board A's bottom parts under
  it (up to 3.55 over the modem), against 5.05 for the normal back.
- **The bump is housed in the keyboard half.** Closed, it sits in a recess in the keyboard half. While swivelling,
  it travels in an arc-shaped channel cut about 10 mm into the keyboard half's top band, the part the screen half
  covers when open, so the channel is never visible. Open, the bump sits in the step above the keyboard half and
  stays within the device's back plane (16 + 9 < 34).
  - For the channel to stay in the key-free band, **the camera must be on the same side as the pivot**. Its closed
    y equals its open x'.
  - The battery must then start at y >= about 31.5: 65 mm tall, y 31.5-96.5, which just fits.
- **Pivot side:**
  - **Left:** the camera would sit over the charger's power stage (Q101-Q104, L101; heat next to the sensor) and
    the microphone port at (82.5, 47.8).
  - **Right (recommended, not decided):** the camera sits at the screen half's top-right corner seen from the front.
    That is board x about 0-30, y about 33-65, right behind its own connector J704 (3.0, 46.5), over the Wi-Fi /
    audio corner. Bottom parts there: speaker sockets 2.96, u.FL J601 / J602 (their cables leave sideways), the
    modem's edge 3.55 at x >= 19.
- **Cost of a right-hand pivot:** the battery harness and the keyboard FFC run about 35-55 mm to the pivot instead
  of about 20-45. The harness grows from <= 80 mm (C2-1, a 25 mV drop budget at 10 A on 26 AWG) to roughly
  120-150 mm.
  - On 24 AWG (D111, 4 wires per polarity), 120 mm stays within that 25 mV budget.
  - 22 AWG (the terminal takes 22-26) allows about 190 mm but is stiffer in the pivot.
- **Camera module (Radxa drawing):**
  - Board 32 x 32 x 1.6 mm with four mounting holes 28 x 28 apart and two holes 20 mm apart beside the lens.
  - Lens block 8.5 x 8.5 x 6.38 mm at the centre.
  - The 31P cable connector is on the **lens side** at one edge, so the cable leaves on the outward face.
  - Parts under 1.5 mm on the back.
  - The standard cable is 150 mm, far longer than needed here, so the excess has to be folded or a shorter cable
    found.

### 2026-11-09: the camera channel checked (`tools/enclosure_swivel.py`, picture `img/camera_channel.png`)

The user asked whether the camera can slide into and out of a cut-out in the keyboard half, making the device
thicker if needed. Yes: that is the channel described above. Computed with the pivot on the right at (76, 22.5),
the camera (34 x 34 with margin) at the screen half's top-right when open:

- **Closed,** the camera lands in the keyboard half's **top-left** corner (x 2-36, y 1-35). The channel it sweeps
  while turning is about 42 x 35 mm in that corner and opens through the keyboard half's top edge. It touches no
  key and stays 40 mm from the pivot; the screen half hides it when open.
- **One clash:** the closed camera reaches y 35, and the battery's top edge is at y 32. Over that 3 mm strip the
  channel (bump 9.3 + 0.5 clearance + 1.0 floor = 10.8 deep) would reach 2.5 mm into the battery's 8 mm.
  The camera's closed y is the half's size minus its open x, so moving the pivot does not help.
- **Fixes:**
  - (a) the keyboard half about 3 mm thicker (closed about 37 mm);
  - (b) both halves about 102 x 102 mm instead of 98.5, thickness unchanged;
  - (c) a battery of at most 61.5 mm instead of 65 (conflicts with E2).

### 2026-11-09: block model v1 and the first printable mock-up

**Files**
- `model/enclosure_open.step`, `model/enclosure_closed.step`: open in any CAD program (FreeCAD, Fusion,
  Onshape). They hold both halves, the boards as part envelopes, the battery, display, keyboard placeholder, rear
  camera and pivot.
- `model/mockup_screen_half.stl` and `model/mockup_keyboard_half.stl`: for printing.
- `img/view_*.png`: pictures.
- To rebuild, first export the board envelopes with KiCad's Python: `python3 tools/board_envelopes.py
  hw/board_a/cm5_carrier.kicad_pcb docs/enclosure/model/board_a_envelope.json`, and the same for board_b. Then run
  `tools/enclosure_model.py OUT_DIR` (needs build123d, shapely, numpy, pillow). All parameters are at the top of
  that script.

**What the model checks**
- **Size:** open 98.5 x 152 x 37.1 mm; closed 98.5 x 98.5 x 37.1 mm.
- **Clearances (all zero overlap):**
  - closed, the camera bump is clear of the keyboard half;
  - the camera is clear of Board A's parts;
  - the display is clear of Board A's parts. The tallest, J102 at 5.9 mm, ends 0.19 mm below the display's back.
    That is tight, and the CM5 height under the heat spreader is UNVERIFIED.

**What it is not**
- The halves are solid blocks: no walls, bosses, clips, cable paths or antenna windows yet.
- The keyboard is a 74 x 53.1 x 3 placeholder (not measured), and the CM5 is a 4.6 mm box (UNVERIFIED).
- There is no front camera.
- The display sits flush with the front; no bezel lip is designed.
- The pivot is an M4 through-bolt. That is for the mock-up only: the real pivot must stay blind on the screen side,
  because the display covers that spot.
- **Known point to rework:** closed, the part of the channel the bump does not fill is open at the top edge, a
  notch of about 8 x 10 mm.

**Printing the mock-up**
- **Orientation:** the files are already oriented. The screen half prints front face down, the keyboard half back
  face down. No supports needed.
- **Settings:** about 0.2 mm layers, 3-4 walls, 10-20 % infill, PLA or PETG.
- **Hardware:** an M4 x 30 socket-head bolt from the back of the keyboard half (7.2 mm counterbore), an M4 nut in the
  hex pocket on the screen half's front, and one M4 washer between the halves. The washer makes the gap about 0.8 mm
  instead of 0.5; the bump keeps 1.3 mm of depth clearance.
- **What to try:**
  - how it feels in the hand and how thick it is;
  - the swivel, and the bump running through its channel;
  - typing reach over the grooved keyboard area;
  - where the ports and buttons fall: recesses on the sides (USB-A x 2 on top; USB-C right; SIM, microSD, POWER,
    VOL+, VOL- left; open positions).

