# VOXF — Voxel Container Format Reference
**Version 1.2.0** · Open Format · 2026 · HADS 1.0.0

---

## AI READING INSTRUCTION

Read `[SPEC]` and `[BUG]` blocks for authoritative facts. Read `[NOTE]` only if additional context is needed. `[?]` blocks are unverified. When implementing a parser, read all `[BUG]` blocks before writing any byte-level code.

---

## 1. OVERVIEW

**[SPEC]**
- Format: binary, little-endian
- Extension: `.voxf`
- Magic bytes: `56 4F 58 46` (ASCII: `VOXF`)
- Max file size: 4 GB (constrained by 32-bit chunk length fields)
- Compression: optional zlib per chunk
- Spec version: stored in header, current = `0x0102` (major=1, minor=2)

**[NOTE]**
VOXF was designed for real-time voxel streaming. The chunk-based layout allows partial reads — a loader can skip to the geometry chunk without reading material or metadata chunks. This is intentional and should be preserved in any writer implementation.

---

## 2. FILE LAYOUT

**[SPEC]**
```
[Header]        32 bytes, always uncompressed
[Chunk 0]       variable length
[Chunk 1]       variable length
...
[Chunk N]       variable length
[EOF marker]    4 bytes: 0x00 0x00 0x00 0x00
```

Chunks may appear in any order except: Header is always first, EOF marker always last.

---

## 3. HEADER

**[SPEC]**
```
Offset  Size  Type    Field
0       4     u8[4]   magic = 0x56 0x4F 0x58 0x46
4       2     u16     spec_version (major<<8 | minor)
6       2     u16     flags (see §3.1)
8       4     u32     chunk_count
12      4     u32     total_voxels
16      8     u64     timestamp (Unix epoch, seconds)
24      4     u32     creator_id (registered app ID, 0 = anonymous)
28      4     u8[4]   reserved = 0x00 0x00 0x00 0x00
```

Total: 32 bytes.

### 3.1 Flags

**[SPEC]**
```
Bit 0: compression_enabled   1 = chunks may be zlib compressed
Bit 1: has_metadata          1 = META chunk present
Bit 2: has_palette           1 = PALT chunk present
Bit 3: streaming_mode        1 = file may be incomplete (for live capture)
Bits 4–15: reserved, must be 0
```

**[NOTE]**
`streaming_mode` (bit 3) is set when the file is written in real-time and may not have a valid EOF marker. Parsers should handle missing EOF marker gracefully when this flag is set.

---

## 4. CHUNK FORMAT

**[SPEC]**
```
Offset  Size  Type    Field
0       4     u8[4]   type_id (ASCII 4-char tag)
4       4     u32     length  (byte length of data field, NOT including header)
8       1     u8      flags   (bit 0: compressed, bits 1–7: reserved)
9       3     u8[3]   reserved = 0x00 0x00 0x00
12      N     u8[N]   data    (N = length)
```

If `flags` bit 0 is set, `data` is zlib-compressed. Decompress before parsing.

### 4.1 Known chunk types

**[SPEC]**
| Type ID | ASCII | Description |
|---------|-------|-------------|
| `0x47454F4D` | `GEOM` | Voxel geometry data (required) |
| `0x4D455441` | `META` | Key-value metadata (optional) |
| `0x50414C54` | `PALT` | Color palette (optional) |
| `0x414E494D` | `ANIM` | Animation keyframes (optional) |
| `0x5448554D` | `THUM` | Thumbnail image (optional) |

Only `GEOM` is required. All others are optional.

---

## 5. GEOM CHUNK

**[SPEC]**
```
Offset  Size  Type    Field
0       2     u16     width   (X axis, voxels)
2       2     u16     height  (Y axis, voxels)
4       2     u16     depth   (Z axis, voxels)
6       2     u16     reserved = 0
8       N     u8[N]   voxel_data
```

`voxel_data` layout: row-major order, X iterates fastest, then Y, then Z.
Each voxel: 4 bytes (`u8 r, u8 g, u8 b, u8 a`). Alpha=0 means empty voxel.

Total voxel_data size: `width × height × depth × 4` bytes.

**[NOTE]**
Empty voxels (alpha=0) are stored explicitly. For sparse volumes this is inefficient — use compression (zlib on the GEOM chunk) to mitigate. A future version will add RLE encoding for empty runs.

**[BUG] width/height/depth values off by one in v1.0 writers**
Symptom: Parsed grid has one extra empty row/column/layer on positive axis edge.
Cause: v1.0 spec was ambiguous — some writers stored `dimension - 1`, others stored `dimension`.
Affected versions: Files written by v1.0 tools only.
Fix: Check `spec_version` in header. If `0x0100`, add 1 to each dimension before allocating grid.

---

## 6. META CHUNK

**[SPEC]**
Key-value store. UTF-8 strings. Format:

```
[entry count: u16]
[entry 0]
[entry 1]
...

Entry format:
  [key length: u16][key: u8[N]]
  [value length: u16][value: u8[N]]
```

Max key length: 255 bytes. Max value length: 65535 bytes. Max entries: 65535.

Reserved keys (do not use for custom data):
```
"title"       Display name of the model
"author"      Creator name
"license"     SPDX license identifier
"app"         Writer application name and version
```

**[?]**
- Behavior when duplicate keys are present — spec is silent. Parsers likely take last value.
- Unicode normalization requirements — not specified. Assume NFC.

---

## 7. PALT CHUNK

**[SPEC]**
```
[entry count: u16]
[entry 0]: u8 r, u8 g, u8 b, u8 a, u16 index
...
```

Maps palette index to RGBA color. GEOM voxel data uses 1-byte palette index instead of 4-byte RGBA when `has_palette` flag is set.

**[NOTE]**
When `has_palette` is set, GEOM `voxel_data` layout changes: each voxel is 1 byte (palette index) instead of 4 bytes (RGBA). Index 0 is always empty (transparent). This can reduce file size by 4× for models with fewer than 256 colors.

**[BUG] PALT chunk ignored by v1.1 reference parser**
Symptom: Colors render as white when PALT chunk is present.
Cause: v1.1 reference parser did not implement palette mode. Bug in parser, not format.
Affected: Reference parser versions 1.1.0–1.1.3. Fixed in 1.1.4.
Fix: Update reference parser to ≥1.1.4, or implement palette lookup in custom parser.

---

## 8. WRITING A VALID FILE

**[SPEC]**
Minimum valid VOXF file:
1. Write 32-byte header with correct magic and `chunk_count = 1`
2. Write one GEOM chunk with voxel data
3. Write EOF marker: `0x00 0x00 0x00 0x00`

Recommended order for optional chunks: `META`, `PALT`, `GEOM`, `ANIM`, `THUM`.
Rationale: parsers that stop after GEOM will still have read metadata.

**[?]**
- Maximum chunk count — u32 field allows ~4 billion, but no implementation has been tested above 1000 chunks.
- ANIM chunk format — referenced in spec header but not yet documented. Do not implement.
