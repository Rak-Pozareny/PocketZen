# Building the hardware from code

Everything in `hw/` and `fab/` is generated: the schematics, footprints, placement, routing and manufacturing files
all come from the scripts in `gen/` and `tools/`. This page explains how to run each step again. The project
overview is in the [README](../README.md), and the documentation index is in [docs/README.md](README.md).

Run every command from the repository root.

## Where each phase stands

| Phase | State | Report |
|---|---|---|
| 1. Research, block diagram, pin budget, power budget | done; every question answered in `docs/DECISIONS.md` | `docs/checkpoint1/CHECKPOINT1.md` |
| 2. Schematics (Board A hierarchical, Board B separate) and ERC | done; ERC 0 errors on both boards | `docs/checkpoint2/CHECKPOINT2.md` |
| 3. Placement, mechanical fit, 3D renders, height check | done; revised after review (cameras, power stages) | `docs/checkpoint3/CHECKPOINT3.md` |
| 4. Routing, DRC, length matching | done; DRC 0 errors, 0 unconnected on both boards | `docs/checkpoint4/CHECKPOINT4.md` |
| 5. Manufacturing files and the pre-manufacture review | done | `fab/board_a/`, `fab/board_b/`, `docs/checkpoint5/CHECKPOINT5.md`, `REVIEW.md` |
| 6. Board A moved to the Orange Pi CM5 | done (D85-D123); ERC 0, DRC 0 errors / 0 unconnected, parity 0, Gerber check pass | `docs/opi/OPI_REDESIGN.md` |
| 7. Both boards ordered | in production at JLCPCB (Board A: order Y5) | `docs/board_status.md` |
| 8. Bring-up plan | written; test-point maps from `tools/tp_map.py` | `docs/bringup/BRINGUP.md` |
| 9. Linux device tree for Orange Pi's 6.1 images | written, not yet tested on hardware; display disabled until the panel driver is added | `software/README.md` |
| 10. Enclosure block model | v2: half-apple shell, printable mock-up | `docs/enclosure/ENCLOSURE.md` |

## Layout

```
gen/                  generators: schematics, footprints, placement, routing (route_*.py, groute.c), length tuning
hw/board_a/           Board A KiCad project (generated: do not edit by hand)
hw/board_b/           Board B KiCad project (generated)
fab/board_a/, fab/board_b/   the JLCPCB order packages: Gerber zip, BOM.csv, CPL.csv, ORDER.md, PDFs, STEP, stack-up
tools/                checks, reports, images and enclosure models (all re-runnable)
docs/checkpoint1-5/   the checkpoint reports from the first (Radxa CM5) design, with tables, PDFs and images
docs/opi/             the Orange Pi CM5 redesign of Board A: report, pin map, block diagram, power tree, length report
docs/bringup/         the bring-up plan and test-point maps
docs/enclosure/       the enclosure decisions, the dimensions it is built from, block models and pictures
docs/media/           the README images
software/             Linux device tree for Board A on Orange Pi's 6.1 images, kernel options, build and check scripts
datasheets/           the datasheets, drawings and reference designs the boards rest on, with an index
research/             extracted text and image crops from the sources, JLCPCB capability and impedance data;
                      the raw downloads (research/dl/) are kept locally, not in git
REVIEW.md             the pre-manufacture review: UNVERIFIED items, assumptions, what to check, cost, parts to buy
```

## Board A (Orange Pi CM5 version)

```
python3 -I tools/opi_pins.py         # Orange Pi pin definition PDF -> gen/data/opi_cm5_pins.json
python3 gen/footprints.py            # footprints, including the Orange Pi DF40 positions
python3 -I gen/build_a.py            # schematics, ERC and netlist check
python3 -I tools/opi_pinmap.py       # docs/opi/opi_cm5_pin_map.csv
python3 -I tools/make_diagrams.py    # docs/opi/block_diagram.svg, power_tree.svg
python3 gen/pcb_a.py                 # placement
python3 gen/route_a.py --out X       # routing (about 6 hours); then install X into hw/board_a and run tools/package.py a
python3 gen/art_a.py hw/board_a/cm5_carrier.kicad_pcb   # logo and text (D106, D121); tools/package.py a runs it too
GERBER_CHECK_PYTHON=VENV/bin/python python3 tools/package.py a   # VENV: a venv with shapely, for tools/gerber_check.py (D116)
python3 tools/pour_cuts.py hw/board_a/cm5_carrier.kicad_pcb LAYER:X:Y ...   # only if the Gerber check reports a pour sliver;
                                     # then tools/refill_pours.py and tools/package.py a again
```

The routing pipeline in `gen/route_a.py` runs these stages in order: rules, power pours, differential pairs, length
tuning, power trunks, ground fan-out, the grid router, and the ground pours. It can also run in two steps:

```
python3 gen/route_a.py --out X --stop-after fanout   # everything before the grid router (about 10 minutes)
python3 gen/route_a.py --out X --resume              # then the grid router and the ground pours
python3 gen/route_a.py --finish      # a run that ended with connections open: the rip-up and clean-up stage again
```

The grid router's C core is compiled with gcc the first time it is used, into
`build/libgroute-<hash of gen/groute.c>.so`.

Board A's routing is not bit-identical between runs. Everything before the grid router is, but two full runs of the
same code diverge in the grid router's second stage. A re-run therefore gives a slightly different routing, with a
different handful of connections left for the rip-up passes. The likely cause is ordering: new tracks get random
IDs, KiCad stores them in ID order, and the negotiation depends a little on the order it meets them in. Not every run
reaches zero open connections (`docs/checkpoint4/CHECKPOINT4.md`, section 5).

## Board B

```
python3 -I gen/build_b.py            # schematics -> hw/board_b
python3 gen/pcb_b.py                 # placement
python3 gen/route_b.py               # ground fan-out, grid router, ground pours (about 8 minutes)
python3 tools/package.py b           # fab/board_b/
```

## The manufacturing packages

`tools/package.py` runs these steps in order:

1. places the silkscreen references (`tools/silk.py`) and copies the schematic's fields and attributes to the
   footprints (`tools/sync_pcb.py`), both in place
2. runs ERC, and DRC with the schematic parity check
3. writes the fab files, the schematic PDF, the STEP model and the stack-up from the files in `hw/`
4. checks every BOM line against JLCPCB's live catalogue and prices it
5. writes `fab/<board>/ORDER.md` with the order options and the check results

Each board takes a few minutes, mostly the live JLCPCB queries.

```
python3 tools/package.py a           # fab/board_a/: cm5_carrier_gerber.zip, BOM.csv, CPL.csv, ORDER.md, ...
python3 tools/package.py b           # fab/board_b/
python3 tools/fab.py BOARD.kicad_pcb OUTDIR NAME     # only the Gerber / drill zip, BOM.csv, CPL.csv, ROTATIONS.md
python3 -I tools/bom_cost.py fab/board_a/BOM.csv     # parts cost at live JLCPCB prices
```

## Checks and reports

```
kicad-cli pcb drc --format json -o OUT.json hw/board_a/cm5_carrier.kicad_pcb
python3 tools/length_report.py hw/board_a/cm5_carrier.kicad_pcb docs/opi/length_report.md
python3 tools/fpcheck.py hw/board_a hw/board_a/cm5_carrier.net    # every pin has a pad and every pad a pin
python3 tools/heights.py hw/board_a/cm5_carrier.kicad_pcb         # tallest parts and the component stack
python3 tools/placement_check.py hw/board_a/cm5_carrier.kicad_pcb # decoupling, switch-node and sensitive-net distances
python3 -I tools/netreport.py hw/board_a cm5_carrier --pairs      # differential-pair polarity
sh tools/copper_plots.sh hw/board_a/cm5_carrier.kicad_pcb OUT_DIR board_a
```

## Images, datasheets and test-point maps

```
python3 -I tools/media.py            # docs/media/: renders with the parts' EasyEDA models (cached in research/dl/easyeda_3d),
                                     # the hero image with its reflection, Board A's six copper layers
sh tools/renders.sh OUT_DIR          # KiCad's own 3D renders of both boards
python3 -I tools/datasheets.py       # datasheets/ and its index, with the BOM coverage check
python3 -I tools/tp_map.py           # docs/bringup/: test-point maps of both boards (reads the boards, changes nothing)
```

## Enclosure

These need build123d, shapely, numpy and pillow.

```
python3 tools/board_envelopes.py BOARD.kicad_pcb OUT.json   # a board's envelope (docs/enclosure/model/board_*_envelope.json)
python3 tools/apple_outline.py       # the outline traced from the to-scale sketch -> docs/enclosure/model/apple_outline.json
python3 tools/enclosure_apple.py OUT_DIR   # block model (STEP), printable mock-up (STL) and pictures
```

## The first (Radxa CM5) design

The checkpoint 1-5 reports describe the design as it was built around the Radxa CM5. Their tools still run on the
Radxa data where they read it, for example `tools/cp1_tables.py`, `tools/cp1_build.py` and `tools/cm5_pinmap.py`.
The finished Radxa version of Board A is kept locally as a snapshot (`archive/README.md`).
