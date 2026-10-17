# `LOC_DATA` Binary Specification, Round-Trip Verification, and JA↔KO Alignment Report

- **Generated**: `2026-10-16` (KST)
- **Target Releases**:
  - **Japanese Original (`ja`)**: `Clank & Ratchet - Maruhi Mission Ignition! (Japan).iso` (`UCJS10084` v1.00)
  - **Official Korean Release (`ko`)**: `Secret Agent Clank [K].iso` (`UCKS45096` v1.00)
- **Verification Script**: `python -B scripts/analyze_localdat.py`
- **Machine-Readable Report**: `qa/reports/localdat_analysis.json`

---

## 1. Executive Summary

1. **Binary Format & Parser Disassembly (`STATIC ANALYSIS`)**:
   - Disassembled the `LOC_DATA` binary container parser in `PSP_GAME/USRDIR/BIN/FRONTEND.PRX` (`0x1cc80..0x1d450` and subtitle timing loader `0x18b6c`) and the custom character decoders in `PSP_GAME/SYSDIR/BOOT.BIN` (`0x9d1c..0xa140`) and `FRONTEND.PRX` (`0xc980..0xce00`).
2. **Unchanged Round-Trip Verification (`BUILD/ROUND-TRIP VERIFIED`)**:
   - `scripts/analyze_localdat.py` parses and re-serializes all four localization binaries (`LOCALDAT_J.BIN`, `LOCALDAT_K.BIN`, `HELPLOCALDAT_J.BIN`, `HELPLOCALDAT_K.BIN`) and all `6,163` string payloads (`2,600 + 2,603 + 480 + 480`) with **100% bit-for-bit SHA-256 identity**.
3. **Full Combinational Hangul Support Confirmed (`STATIC ANALYSIS`)**:
   - The Korean executable (`UCKS45096` `BOOT.BIN` at `0x9f90..0xa11c` and `FRONTEND.PRX` at `0xca10..0xcb9c`) dynamically decomposes 2-byte big-endian Hangul syllables (`0xAC00..0xD7A3`) into Choseong/Jungseong/Jongseong (`/ 28`, `/ 21`). All **11,172 modern Hangul syllables (`가..힣`)** are supported without glyph-table restrictions.
4. **100% Deterministic JA↔KO Alignment (`STATIC ANALYSIS`)**:
   - `HELPLOCALDAT_J.BIN` (`480` entries) and `HELPLOCALDAT_K.BIN` (`480` entries) match `1:1` across all negative IDs `-1..-480`.
   - `LOCALDAT_J.BIN` (`2,600` entries) and `LOCALDAT_K.BIN` (`2,603` entries) align `100%` deterministically once the `3` Korean-only demo menu entries inserted at `KO ID 637..639` (`"메인 메뉴"`, `"메인 메뉴"`, `"데모 게임 종료하기"`) and the resulting `+3` ID shift on `JA ID 637..838` and `2501..2502` are accounted for.

---

## 2. `LOC_DATA` Binary Container Specification

Verified directly from `FRONTEND.PRX` (`0x1ce00..0x1d370` and `0x18b6c`):

### 2.1 Header (`0x00..0x44`, 68 bytes)

| Offset | Size | Type | Field | Description |
| --- | --- | --- | --- | --- |
| `0x00` | `8` | `char[8]` | `magic` | Always `"LOC_DATA"` |
| `0x08` | `4` | `uint32` | `version_flags` | `0x12060101` (`LOCALDAT_*`) or `0x12060105` (`HELPLOCALDAT_*`). Bit 0 (`& 1`): has 4-byte ASCII tags (`SCOL`, `LTOC`, `TDEF`, `ENTR`). Bit 2 (`& 4`): allows signed negative IDs (`HELPLOCALDAT_*`). |
| `0x0C` | `4` | `uint32` | `count_lang` | `(entry_count << 8) \| num_languages` (`num_languages = 1`). |
| `0x10` | `4` | `char[4]` | `scol_tag` | `"SCOL"` |
| `0x14` | `32` | `uint32[8]` | `colors` | 8 RGBA color slots referenced by `<COL:01>..<COL:08>`. |
| `0x34` | `4` | `char[4]` | `ltoc_tag` | `"LTOC"` |
| `0x38` | `12` | `uint32[3]` | `ltoc_a, ltoc_b, ltoc_c` | `ltoc_a = 0x44` (offset of active language block); `ltoc_b` = byte size read by `fread(buf, 1, ltoc_b, fp)` starting at `0x44`; `ltoc_c` = offset relative to `0x44` where the subtitle timing table begins (`0x44 + ltoc_c`, 4-byte aligned). |

### 2.2 `TDEF` Index Table (`0x44 .. 0x44 + entry_count * 12`)

Each entry is 12 bytes (`<4siI`):
- `tag` (`4` bytes): `"TDEF"`
- `text_id` (`int32`): String ID (`1..8063` in `LOCALDAT_*`, `-1..-480` in `HELPLOCALDAT_*`)
- `offset_from_0x40` (`uint32`): Offset relative to `0x40` (`0x40 + offset_from_0x40` points to `"ENTR"`, and `0x44 + offset_from_0x40` points to the first payload byte).

### 2.3 `ENTR` String Table (`0x44 + entry_count * 12 .. 0x44 + ltoc_c`)

Each record starts with `"ENTR"` (`4` bytes) followed by its payload:
1. **Format 1 — `utf8_savedata` (`51` entries in `LOCALDAT_J` and `LOCALDAT_K`, `0` in `HELPLOCALDAT`)**:
   - Used for PSP `sceUtilitySavedata` titles and details (`JA IDs 724..731, 749..791` / `KO IDs 727..734, 752..794`).
   - Layout: `0x00` + `uint8(len(utf8_bytes) + 2)` + `utf8_bytes` + `0xC0 0x80` (Modified UTF-8 null terminator).
2. **Format 2 — `hud_string` (all remaining entries)**:
   - Custom-encoded byte sequence terminated by `0x00`.
   - After the final `ENTR` record's `0x00` terminator, `0..3` zero padding bytes align `0x44 + ltoc_c` to a 4-byte boundary.

### 2.4 Subtitle Timing Table (`0x44 + ltoc_c .. 0x44 + ltoc_b`) & Post-`ltoc_b` Tail

- Parsed by `FRONTEND.PRX` at `0x18b6c`:
  - Header `<3I`: `(n1, n2, n3)`
  - Payload: `n1` `uint32` values + `n2` `uint32` values + `n3` pairs of `(string_id: uint32, frame_time: uint32)` (`12 + 4*n1 + 4*n2 + 8*n3` bytes).
  - In `LOCALDAT_J.BIN` and `LOCALDAT_K.BIN`: `n1=17, n2=68, n3=442` (`3,888` bytes, **100% byte-identical between JA and KO**).
  - In `HELPLOCALDAT_J.BIN` and `HELPLOCALDAT_K.BIN`: `n1=1, n2=1, n3=0` (`20` bytes, **100% byte-identical between JA and KO**).
- **Post-`ltoc_b` Tail**:
  - `LOCALDAT_J.BIN` has `348` trailing bytes and `LOCALDAT_K.BIN` has `220` trailing bytes after `0x44 + ltoc_b` (uninitialized exporter buffer tail never read by `fread(buf, 1, ltoc_b, fp)`). Preserved in `post_ltoc_tail_hex` for bit-exact round-trip verification.

---

## 3. Character Encoding & Control Token Specification

### 3.1 Control & Icon Tokens (`BOOT.BIN` `0x9d1c..0xa140`)

| Byte Sequence | Token Representation | Meaning |
| --- | --- | --- |
| `0x90 XX` | `<COL:XX>` | Color index switch (`<COL:01>` default, `<COL:02>` highlight) |
| `0x91 XX` | `<SCALE:XX>` | Text scale/style parameter (`<SCALE:06>`, `<SCALE:09>`) |
| `0x80` | `<BTN_CROSS>` | PSP Cross (`×`) button icon |
| `0x81` | `<BTN_SQUARE>` | PSP Square (`□`) button icon |
| `0x82` | `<BTN_TRIANGLE>` | PSP Triangle (`△`) button icon |
| `0x83` | `<BTN_CIRCLE>` | PSP Circle (`○`) button icon |
| `0x86` | `<ICON_86>` | Special HUD icon `0x86` |
| `0x89` | `<ELLIPSIS>` | Horizontal ellipsis (`…`) |
| `0x8A` | `<ICON_8A>` | Special HUD icon `0x8A` |
| `0x8B` | `<ICON_8B>` | Special HUD icon `0x8B` |
| `0x9E` | `<BTN_L>` | PSP `L` button icon |
| `0x9F` | `<BTN_R>` | PSP `R` button icon |
| `0xA4` | `<SYM_TM>` | Trademark symbol (`™`) |

### 3.2 Korean Combinational Hangul Encoding (`UCKS45096`)

- **Lead byte range**: `0xAC <= b0 <= 0xD7` (2-byte big-endian Unicode Hangul syllable `U+AC00..U+D7A3`).
- **Null-Byte Escape (`0xD7AC..0xD7D7`)**:
  - Because `hud_string` entries are C-strings terminated by `0x00`, any Hangul syllable whose low byte is `0x00` (`U+AC00` `'가'`, `U+AD00` `'관'`, `U+AE00` `'글'`, ..., `U+D700` `'휀'`) cannot contain a literal `0x00` byte.
  - Such syllables (`code = 0xXX00` where `0xAC <= XX <= 0xD7`) are stored as **`0xD7 XX`** (`0xD7AC..0xD7D7`).
  - At runtime (`BOOT.BIN` `0x9fa0..0x9fb8`, `FRONTEND.PRX` `0xca24..0xca3c`), when `0xD7AC <= code <= 0xD7D7`, the game executes `code = (code & 0xFF) << 8` before decomposing the syllable into Choseong/Jungseong/Jongseong.

### 3.3 Japanese Kana Encoding (`UCJS10084`)

- Uses 2-byte `0x93 XX` sequences:
  - Hiragana (`0x41 <= XX <= 0x93`) and Katakana (`0xA1 <= XX <= 0xFC`) map to `chr(0x3000 + XX)`.
  - Punctuation specials: `0x93 0x01` = `、`, `0x93 0x02` = `。`, `0x93 0x0C` = `「`, `0x93 0x0D` = `」`, `0x93 0x27` = `〜`, `0x93 0x28` = `！`, `0x93 0x29` = `？`, `0x93 0x2A` = `♪`.

---

## 4. Round-Trip Verification Summary

| File | Entries | Size (Bytes) | Original SHA-256 | Rebuilt SHA-256 | Match |
| --- | ---: | ---: | --- | --- | --- |
| `LOCALDAT_J.BIN` | `2,600` | `185,200` | `4b3b73d9bd29cb2bec69cccbca3635081d5d3d914745ac2fb04cb2d0d39708ba` | `4b3b73d9bd29cb2bec69cccbca3635081d5d3d914745ac2fb04cb2d0d39708ba` | **PASS (100%)** |
| `LOCALDAT_K.BIN` | `2,603` | `157,320` | `4d6ef0ca53978a32766da826d2f6283ddc96bc171124d3533d8d50c66c8ec0ae` | `4d6ef0ca53978a32766da826d2f6283ddc96bc171124d3533d8d50c66c8ec0ae` | **PASS (100%)** |
| `HELPLOCALDAT_J.BIN` | `480` | `43,360` | `d96078f6ad4613d335d97a68243824f093fcd3a871be2cb4b43da6998be05330` | `d96078f6ad4613d335d97a68243824f093fcd3a871be2cb4b43da6998be05330` | **PASS (100%)** |
| `HELPLOCALDAT_K.BIN` | `480` | `34,992` | `6831569ab44b42c0b051ea2fd5ab0b4763d1447a464bd90bb8e14fcffa4598e7` | `6831569ab44b42c0b051ea2fd5ab0b4763d1447a464bd90bb8e14fcffa4598e7` | **PASS (100%)** |

---

## 5. JA↔KO ID Alignment & Initial QA Findings in `UCKS45096`

### 5.1 Deterministic ID Mapping (`LOCALDAT_J.BIN` ↔ `LOCALDAT_K.BIN`)

- **3 Korean-only Demo Menu Strings Inserted at `KO ID 637..639`**:
  - `KO ID 637`: `"메인 메뉴"`
  - `KO ID 638`: `"메인 메뉴"`
  - `KO ID 639`: `"데모 게임 종료하기"`
- **Resulting `+3` Shift in Sequential Pool (`204` entries)**:
  - `JA ID 637..835` (`199` entries) $\rightarrow$ `KO ID 640..838` (`KO ID = JA ID + 3`)
  - `JA ID 836..838` (`3` entries) $\rightarrow$ `KO ID 2501..2503`
  - `JA ID 2501..2502` (`2` entries) $\rightarrow$ `KO ID 2504..2505` (`KO ID = JA ID + 3`)
- **All Other IDs (`2,396` in `LOCALDAT` + `480` in `HELPLOCALDAT`)**:
  - `KO ID == JA ID` (`1:1` identical IDs).

### 5.2 Notable Bugs & Untranslated Remnants Found in Official Korean Release (`UCKS45096`)

1. **Broken Button Icon Macros in `HELPLOCALDAT_K.BIN`**:
   - `ID -102`: `"이 우산은 <COL:02>전기<COL:01>를 비축하고 있어요! _[circlebutton]을 눌러 하나의 대상을 공격하거나 _[circlebutton]을 누른 상태로 에너지를 모아 다수를 공격하세요."` (unconverted `_[circlebutton]` literal instead of `<BTN_CIRCLE>`).
   - `ID -103`: `"\"<COL:02>타이어랑<COL:01>\"을 사용해 보안 로봇들을 처치하세요! (던지려면 _[crclesymbol])"` (typo `_[crclesymbol]` instead of `<BTN_CIRCLE>`).
2. **Untranslated English System Strings in `LOCALDAT_K.BIN`**:
   - `KO ID 742` (`JA ID 739`): `"Progress is saving. Do not remove your Memory Stick<SYM_TM> or turn off your PSP<SYM_TM> when the Memory Stick<SYM_TM> access indicator is flashing."`
   - `KO ID 743` (`JA ID 740`): `"Changes and data are saving. When you see this icon on the screen, do not remove your Memory Stick<SYM_TM>, or turn off your PSP<SYM_TM>."`
   - `KO ID 587` (`JA ID 587`): `"CREDITS"` (JA: `"クレジット"`).
3. **Typos in `LOCALDAT_K.BIN`**:
   - `KO ID 618` & `KO ID 624`: `"그레이트 킬l!"` (stray ASCII lowercase `l` before `!`).
4. **Circle/Cross Button Icon Prompt Differences (`36` entries in `LOCALDAT`)**:
   - Because the official Korean text was translated from the North American script (where Cross is Confirm) while the Japanese text uses Circle for Confirm, `36` UI prompt entries differ between `<BTN_CIRCLE>` and `<BTN_CROSS>`. When updating the Korean text from the Japanese script, we must preserve `UCKS45096`'s actual runtime button bindings (only fixing genuine macro bugs like `ID -102` and `ID -103`).

