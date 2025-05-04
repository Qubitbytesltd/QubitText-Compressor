# QubitText Compressor

A Python-based fixed-length text compressor developed by **Qubitbytes Ltd**. It encodes text using variable bit-length codes based on a custom alphabet in `table.txt`, defaulting to `a-z,space` (27 chars + EOS, 5 bits) for broad compatibility, or smaller alphabets (e.g., 8 chars + EOS, 4 bits) for better compression. It uses a dynamic end-of-stream (EOS) marker and no metadata, achieving a compression ratio of 1.38 for `"hello world"` (11 bytes to 8 bytes) with the default `a-z,space` table.

## Features

- **Variable Bit Encoding**: Uses `ceil(log2(N + 1))` bits per character, where `N` is the table size (e.g., 5 bits for 27 chars, 4 bits for 8 chars).
- **No Metadata**: Output (`compressed.hex`) contains only the bitstream and EOS, minimizing size.
- **Table-Based**: Requires `table.txt` (default: `a,b,c,...,z,space`) for encoding/decoding, with the same table needed for both.
- **Compression Ratio**: 1.38 for `"hello world"` (11 bytes → 8 bytes, 55-bit bitstream + 5-bit EOS with default table).
- **Multiple Texts**: Encode multiple texts into separate `.hex` files, decode with matching `table.txt`.
- **Stats**: Reports original size, compressed size (bytes/bits), bitstream size, and ratio.
- **No Dependencies**: Uses only Python standard library.

## Setup

1. **Install Python**: Ensure Python 3.x is installed ([python.org](https://www.python.org/)).
2. **Clone Repository**:
   ```bash
   git clone https://github.com/yourusername/QubitText-Compressor.git
   cd QubitText-Compressor
   ```
