import argparse
import os
import math

class TextCompressor:
    def __init__(self, table_file="table.txt"):
        # Read character set from table file
        self.char_set = []
        with open(table_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            # Handle comma-separated or one-per-line
            if ',' in content:
                chars = content.split(',')
            else:
                chars = content.splitlines()
            for char in chars:
                char = char.strip()
                if char:  # Handle 'space' or ' '
                    if char == 'space':
                        char = ' '
                    self.char_set.append(char.lower())
        
        if not self.char_set:
            raise ValueError("Table file is empty or invalid")
        
        # Calculate bits per character (include EOS)
        self.num_chars = len(self.char_set)
        self.bits_per_char = math.ceil(math.log2(self.num_chars + 1))  # +1 for EOS
        if self.bits_per_char > 5:
            raise ValueError(f"Table has {self.num_chars} chars, requiring {self.bits_per_char} bits/char; max 5 bits supported")
        
        # Create char-to-code and code-to-char mappings
        self.char_to_code = {char: format(i, f'0{self.bits_per_char}b') 
                            for i, char in enumerate(self.char_set)}
        self.code_to_char = {v: k for k, v in self.char_to_code.items()}
        # Add EOS marker
        self.eos_code = format(self.num_chars, f'0{self.bits_per_char}b')  # Highest code
        self.code_to_char[self.eos_code] = None  # None indicates EOS

    def compress(self, text):
        # Convert input to lowercase
        text = text.lower()
        
        # Validate input
        for char in text:
            if char not in self.char_to_code:
                raise ValueError(f"Unsupported character: '{char}'")
        
        # Encode text
        bitstream = ''
        for char in text:
            bitstream += self.char_to_code[char]
        
        # Append EOS marker
        bitstream += self.eos_code
        
        # Convert to bytes (pad to multiple of 8 bits)
        compressed = bytearray()
        for i in range(0, len(bitstream), 8):
            byte_str = bitstream[i:i+8]
            if len(byte_str) < 8:
                byte_str += '0' * (8 - len(byte_str))
            compressed.append(int(byte_str, 2))
            
        return compressed, len(bitstream) - self.bits_per_char  # Bitstream size excludes EOS

    def decompress(self, compressed):
        # Convert bytes to bitstream
        bitstream = ''
        for byte in compressed:
            bitstream += format(byte, '08b')
        
        # Decode until EOS
        text = ''
        i = 0
        while i < len(bitstream):
            code = bitstream[i:i + self.bits_per_char]
            if len(code) < self.bits_per_char:
                break  # Incomplete code, likely padding
            if code == self.eos_code:
                break  # Stop at EOS
            if code in self.code_to_char and self.code_to_char[code] is not None:
                text += self.code_to_char[code]
            else:
                raise ValueError(f"Invalid code: {code}")
            i += self.bits_per_char
        
        return text

def calculate_metrics(original, compressed, bitstream_bits):
    orig_size_bytes = len(original.encode('utf-8'))
    comp_size_bits = len(compressed) * 8  # Total file size in bits
    comp_size_bytes = len(compressed)
    compression_ratio = orig_size_bytes / comp_size_bytes if comp_size_bytes else float('inf')
    
    return {
        'original_size_bytes': orig_size_bytes,
        'compressed_size_bytes': comp_size_bytes,
        'compressed_size_bits': comp_size_bits,
        'bitstream_bits': bitstream_bits,
        'compression_ratio': compression_ratio
    }

def bytes_to_hex(compressed):
    # Format as 0xNN, comma-separated
    return ','.join(f'0x{byte:02x}' for byte in compressed)

def main():
    parser = argparse.ArgumentParser(description="QubitText Compressor: Variable Bit-Length Encoder/Decoder with EOS")
    parser.add_argument("mode", choices=["encode", "decode"], help="Mode: encode or decode")
    parser.add_argument("--file", help="Input file (txt for encode, hex for decode)")
    parser.add_argument("--text", help="Direct text input for encoding or hex for decoding")
    parser.add_argument("--table", default="table.txt", help="Table file with character set")
    
    args = parser.parse_args()
    compressor = TextCompressor(table_file=args.table)
    
    if args.mode == "encode":
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        elif args.text:
            text = args.text
        else:
            print("Error: Provide --file or --text for encoding")
            return
        
        compressed, bitstream_bits = compressor.compress(text)
        metrics = calculate_metrics(text.lower(), compressed, bitstream_bits)
        
        # Save as formatted hex (0xNN,0xNN)
        hex_output = bytes_to_hex(compressed)
        hex_file = "compressed.hex"
        with open(hex_file, 'w', encoding='utf-8') as f:
            f.write(hex_output)
        
        # Save as raw bytes
        byte_file = "bytestream.txt"
        with open(byte_file, 'wb') as f:
            f.write(compressed)
        
        print(f"Bits per Character: {compressor.bits_per_char}")
        print(f"Original Size: {metrics['original_size_bytes']} bytes")
        print(f"Compressed Size: {metrics['compressed_size_bytes']} bytes ({metrics['compressed_size_bits']} bits)")
        print(f"Bitstream Size: {metrics['bitstream_bits']} bits")
        print(f"Compression Ratio: {metrics['compression_ratio']:.2f}")
        print(f"Compressed hex output saved to {hex_file}")
        print(f"Compressed byte stream saved to {byte_file}")
    
    elif args.mode == "decode":
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                hex_input = f.read().strip()
            # Handle 0xNN,0xNN format or plain hex
            if hex_input.startswith('0x'):
                # Parse comma-separated 0xNN values
                hex_values = hex_input.split(',')
                compressed = bytearray(int(h, 16) for h in hex_values)
            else:
                compressed = bytes.fromhex(hex_input)
        elif args.text:
            compressed = bytes.fromhex(args.text)
        else:
            print("Error: Provide --file or --text for decoding")
            return
        
        # Decode
        decompressed = compressor.decompress(compressed)
        
        # Calculate metrics
        bitstream_bits = len(decompressed) * compressor.bits_per_char
        metrics = calculate_metrics(decompressed, compressed, bitstream_bits)
        
        # Save output
        output_file = "decompressed.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(decompressed)
        
        # Print stats and content
        print(f"Bits per Character: {compressor.bits_per_char}")
        print(f"Decompressed text saved to {output_file}")
        print(f"Original Size: {metrics['original_size_bytes']} bytes")
        print(f"Compressed Size: {metrics['compressed_size_bytes']} bytes ({metrics['compressed_size_bits']} bits)")
        print(f"Bitstream Size: {metrics['bitstream_bits']} bits")
        print(f"Compression Ratio: {metrics['compression_ratio']:.2f}")
        print(f"Decompressed Content: {decompressed}")

if __name__ == "__main__":
    main()