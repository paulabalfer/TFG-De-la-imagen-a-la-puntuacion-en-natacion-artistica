import random
import os

INPUT_FILE = "all_files.txt"
NUM_FILES = 25
IMAGES_PER_FILE = 263
OUTPUT_DIR = "splits"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(INPUT_FILE, "r") as f:
    all_images = [line.strip() for line in f if line.strip()]

print(f"Total images in pool: {len(all_images)}")

# Build a flat list of (file_index, image) assignments by shuffling all images
# and distributing them into slots, then shuffling each file's images independently.
# This ensures no positional or sequential pattern.

total_slots = NUM_FILES * IMAGES_PER_FILE  # 6575

# Sample without replacement across all slots so every slot gets a unique image
# (pool has 6576 images, we need 6575 — one image won't appear)
chosen = random.sample(all_images, total_slots)

# Assign to files: instead of sequential slicing (which would be a pattern),
# shuffle the chosen list again and then assign in random chunks
random.shuffle(chosen)

# Split into 25 chunks of 263, then shuffle each chunk individually
chunks = [chosen[i * IMAGES_PER_FILE:(i + 1) * IMAGES_PER_FILE] for i in range(NUM_FILES)]
for chunk in chunks:
    random.shuffle(chunk)

# Write files in a random order of chunk assignment (file index != chunk index)
file_order = list(range(NUM_FILES))
random.shuffle(file_order)

for file_num, chunk_idx in enumerate(file_order, start=1):
    out_path = os.path.join(OUTPUT_DIR, f"batch_{file_num:02d}.txt")
    with open(out_path, "w") as f:
        f.write("\n".join(chunks[chunk_idx]) + "\n")
    print(f"Wrote {out_path} ({len(chunks[chunk_idx])} images)")

print("Done.")
