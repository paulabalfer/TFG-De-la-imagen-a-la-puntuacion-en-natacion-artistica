import random
import os
import math

INPUT_FILE = "data/all_files.txt"
IMAGES_PER_FILE = 250
OUTPUT_DIR = "splits"
RANDOM_SEED = 42

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(INPUT_FILE, "r") as f:
    all_images = [line.strip() for line in f if line.strip()]

total_images = len(all_images)
print(f"Total images in pool: {total_images}")

random.seed(RANDOM_SEED)
random.shuffle(all_images)

num_files = math.ceil(total_images / IMAGES_PER_FILE)
print(f"Files needed: {num_files}")

for file_num in range(num_files):
    start = file_num * IMAGES_PER_FILE
    end = start + IMAGES_PER_FILE
    chunk = all_images[start:end]

    out_path = os.path.join(OUTPUT_DIR, f"batch_{file_num + 1:02d}.txt")
    with open(out_path, "w") as f:
        f.write("\n".join(chunk) + "\n")

    print(f"Wrote {out_path} ({len(chunk)} images)")

print("Done.")
