# Official self-hosted font assets

Retrieved 2026-10-07 with GitHub CLI official API. No package installation, system font changes, or website edits. Do not ship SourceHanSansSC-VF.woff2 as a monolithic browser font.

| Asset | Bytes | Verified identity / axes |
| --- | ---: | --- |
| Archivo-Variable.ttf | 658596 | Archivo SemiBold; wght 100–900 (default 600), wdth 62–125 (default 100); 653 encoded characters |
| Archivo-Variable.woff2 | 189528 | Complete lossless WOFF2 conversion of the above, recommended over restricted Latin subset |
| Archivo-Variable-Latin.woff2 | 120776 | Optional restricted U+0000–024F and U+2000–206F subset; same two axes; 424 characters |
| IBMPlexMono-Regular.woff2 | 49248 | Official complete IBM Plex Mono Regular; static 400; 1049 characters |
| IBMPlexMono-Medium.woff2 | 50400 | Official complete IBM Plex Mono Medm; static 500; 1049 characters |
| SourceHanSansSC-VF.woff2 | 14129688 | Official Source Han Sans SC VF; wght 250–900; 44853 encoded characters |

## Source URLs and licenses

- Archivo: https://github.com/Omnibus-Type/Archivo/blob/211127690e8ff106c36c935f7e5e697114cff103/fonts/variable/Archivo%5Bwdth%2Cwght%5D.ttf ; `Archivo-OFL.txt` from https://github.com/Omnibus-Type/Archivo/blob/211127690e8ff106c36c935f7e5e697114cff103/OFL.txt . SIL OFL 1.1, no declared Reserved Font Name.
- IBM: https://github.com/IBM/plex/tree/763c36ef9117782905ae010056dfbe8fd2653a25/packages/plex-mono/fonts/complete/woff2 ; `IBM-Plex-OFL.txt` from that directory's `license.txt`. SIL OFL 1.1; Reserved Font Name Plex. These two files remain unmodified official files, so original name is permitted.
- Adobe: https://github.com/adobe-fonts/source-han-sans/blob/a4f7cf94edfb9d7ffbdfc4841de276358bd7e0f2/Variable/WOFF2/TTF/SourceHanSansSC-VF.ttf.woff2 ; `Source-Han-Sans-OFL.txt` from https://github.com/adobe-fonts/source-han-sans/blob/a4f7cf94edfb9d7ffbdfc4841de276358bd7e0f2/LICENSE.txt . SIL OFL 1.1; Reserved Font Name Source.

All copyright and license texts must accompany distribution. Adobe subsets are modified fonts: rename the internal family, full, PostScript, typographic family and variable instance names to a project-specific name without Source, e.g. Offset Han Sans. Keep original copyright and license name records. If IBM is ever subsetted, rename away from Plex too. Archivo need not be renamed.

## Distributed Chinese subsets

The website ships 3 disjoint current-content subsets named Offset Han Sans, totaling 453688 bytes and covering 1010 codepoints used by the current curated pages and UI. The original 14 MB font and optional Archivo Latin subset are not distributed. Rebuild the subsets when content changes; system CJK fonts cover other characters.

Internal font family, full, PostScript and variable instance names were renamed away from Source. Original copyright and license records remain intact. `prepare_fonts.py` uses FontTools with Brotli, preserves the variable weight axis and layout features, and verifies the subset cmap and names. `assets/fonts/NOTICE.txt` records the derivative relationship.

## SHA-256

Archivo-Variable.ttf: 664bbeb10522dac35c174a3860aaecad7b1ad3a0fc8b0d26888e26c824ec556d

Archivo-Variable.woff2: 1a4bb3b47e7922c13291e556dc9ebb738c852531e7aeda72ef7dcb9d5c941af6

IBMPlexMono-Regular.woff2: ba204497f16b6d334cee9d1e963a831b73e3a56e1d6300a8489d18df7214b350

IBMPlexMono-Medium.woff2: 33faf307fa6031fb4062276d7320a6d632de890cbb347576fd80cfa01077bc25

SourceHanSansSC-VF.woff2: cfec773cdc2ea964de8713471c6fd20774bc40617f5567f92efeeccaca6604b0
