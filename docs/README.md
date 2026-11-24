# Documentation

An index of the documents in this repository. The project overview is in the [README](../README.md).

## Start here

| Document | What it is |
|---|---|
| [`DECISIONS.md`](DECISIONS.md) | the decision log: the 22 design questions (Q1-Q13, C-items) and 123 decisions (D1-D123), each with the alternatives, the reason and the sources |
| [`../REVIEW.md`](../REVIEW.md) | the pre-manufacture review: what is verified, what is assumed, what is still open, and what an experienced engineer should check |
| [`board_status.md`](board_status.md) | where the boards and orders stand, what is waiting on whom, and notes for bring-up |
| [`bringup/BRINGUP.md`](bringup/BRINGUP.md) | the bring-up plan: power-up in stages, the expected value at every test point, test-point maps, record sheets |
| [`BUILDING.md`](BUILDING.md) | how the design is generated from code, and how to run each step again |

## The design, in the order it was made

| Document | Contents |
|---|---|
| [`checkpoint1/CHECKPOINT1.md`](checkpoint1/CHECKPOINT1.md) | research, block diagram, pin budget, power budget, parts shortlist |
| [`checkpoint2/CHECKPOINT2.md`](checkpoint2/CHECKPOINT2.md) | schematics of both boards, electrical-rule check |
| [`checkpoint3/CHECKPOINT3.md`](checkpoint3/CHECKPOINT3.md) | placement, mechanical fit, 3D renders, component height check |
| [`checkpoint4/CHECKPOINT4.md`](checkpoint4/CHECKPOINT4.md) | routing, stack-up and impedance, length matching, design-rule check |
| [`checkpoint5/CHECKPOINT5.md`](checkpoint5/CHECKPOINT5.md) | manufacturing outputs |
| [`orange_pi_cm5_check.md`](orange_pi_cm5_check.md) | the Orange Pi CM5 checked pin by pin against the carrier, after the Radxa CM5 turned out not to be buyable |
| [`opi/OPI_REDESIGN.md`](opi/OPI_REDESIGN.md) | Board A redesigned for the Orange Pi CM5: changes, results, block diagram and power tree |
| [`opi/length_report.md`](opi/length_report.md) | every differential pair's length and skew against its target, with the source of each target |
| [`footprint_audit.md`](footprint_audit.md) | the 24 project footprints checked against their datasheet drawings |

Checkpoints 1-5 cover the first design, built around the Radxa CM5. The Orange Pi documents cover how Board A
changed when it moved to the Orange Pi CM5, which is the version in production.

## Manufacturing and verification

| Document | Contents |
|---|---|
| [`../fab/board_a/ORDER.md`](../fab/board_a/ORDER.md), [`../fab/board_b/ORDER.md`](../fab/board_b/ORDER.md) | what to upload, every option on the order page, and the checks run on exactly those files |
| [`../fab/board_a/STACKUP.md`](../fab/board_a/STACKUP.md), [`../fab/board_a/IMPEDANCE.md`](../fab/board_a/IMPEDANCE.md) | Board A's stack-up and controlled-impedance classes |
| [`../tools/jlc_prod_check/README.md`](../tools/jlc_prod_check/README.md) | the manufacturer's production files compared with this design before the order was confirmed |

## Parts, enclosure and software

| Document | Contents |
|---|---|
| [`off_board_parts.md`](off_board_parts.md) | everything that plugs in or screws on: compute module, modem, battery, display, cameras, cables |
| [`shopping_list_eu.md`](shopping_list_eu.md) | where those parts can be bought for delivery in the EU, with prices seen and caveats |
| [`../datasheets/README.md`](../datasheets/README.md) | index of the datasheets, drawings and reference designs, by board |
| [`enclosure/ENCLOSURE.md`](enclosure/ENCLOSURE.md) | the enclosure: decisions E1-E12, open questions, the half-apple block models and their fit checks |
| [`enclosure/mechanical_inputs.md`](enclosure/mechanical_inputs.md) | the board and part dimensions the enclosure is built from |
| [`../software/README.md`](../software/README.md) | the Linux device tree for Board A on Orange Pi's images (written, not yet tested on hardware) |
| [`../archive/README.md`](../archive/README.md) | a list of the snapshots taken before the project moved to git (the snapshots themselves are not published) |
