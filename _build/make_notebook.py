"""Generate notebooks/01_baseline_droppings_classifier.ipynb.

The notebook is written here as plain cell sources so it can be diffed and
regenerated. Run:  python _build/make_notebook.py
"""
import json
import pathlib

CELLS = []


def md(src):
    CELLS.append({"cell_type": "markdown", "metadata": {}, "source": src.strip("\n")})


def code(src):
    CELLS.append({"cell_type": "code", "metadata": {}, "execution_count": None,
                  "outputs": [], "source": src.strip("\n")})


# --------------------------------------------------------------------------
md(r"""
# Orora AgriTech: droppings classifier (model v1)

**Goal:** a small image model that sorts a photo into five classes: four kinds of chicken droppings (healthy, coccidiosis, salmonellosis, Newcastle disease) plus **"not droppings"**, so the app can refuse a photo of a floor, a hand or a table instead of calling it healthy. It must run **offline on an entry-level phone**. This notebook trains it, measures it honestly, and exports it for the demo app.

**Run it on Google Colab with a GPU** (Runtime → Change runtime type → T4 GPU). The datasets download straight to the Colab machine, so nothing large crosses your own connection.

| Step | What happens | Time (T4, approx.) |
|---|---|---|
| 1–3 | Droppings images: download from Zenodo, resize, cache to Google Drive | 2–3 hours the first time; a few minutes after that |
| 3b | "Not droppings" images: objects and textures from public research datasets | 5–10 min |
| 4–5 | Duplicate check; split into train / validation / test | a few min |
| 6–7 | Train MobileNetV3-Small in two phases | 20–30 min |
| 8 | Evaluate per class, on the test set and on the lab-confirmed (PCR) set; check the "not droppings" guard | 1 min |
| 9–10 | Export TFLite (float16 for the web app, int8 for phones) and check it agrees with the model | a few min |
| 11 | Optional: test on Orora's own photos | 1 min |
| 12 | Package `app_model.zip` and download it | 1 min |

**Data.** Credit the authors wherever the model is shown.
- Machuve D., Nwankwo E., Lyimo E., Maguo E., Munisi C.: *Machine Learning Dataset for Poultry Diseases Diagnostics*, Zenodo, v2 ([10.5281/zenodo.4628934](https://doi.org/10.5281/zenodo.4628934)), CC BY 4.0. 6,812 farm-labelled images; the training source.
- The same authors: v3, PCR-annotated ([10.5281/zenodo.5801834](https://doi.org/10.5281/zenodo.5801834)), CC BY 4.0. 1,255 images whose labels were confirmed by laboratory PCR. **Used only as a second, stricter test set, never for training.**
- "Not droppings": Imagenette (a subset of ImageNet, fast.ai) and the Describable Textures Dataset (Cimpoi et al., Oxford). Both are for **research use**: fine for this prototype, but replace them with Orora's own photos (feed, litter, floors, birds, hands) before any commercial use. Put those in Drive under `Orora AgriTech/other_training/` and they are added automatically.

**Caveat.** Newcastle disease is the rarest class (376 images in v2), so its score matters more than the overall average.
""")

# --------------------------------------------------------------------------
md("## 0 · Setup")
code(r"""
!nvidia-smi -L || echo "No GPU: Runtime > Change runtime type > T4 GPU"
!pip -q install imagehash
import os, json, glob, shutil, subprocess, tarfile, random, time, pathlib, concurrent.futures as cf
import numpy as np, pandas as pd
import tensorflow as tf
import keras
from PIL import Image, ImageOps
import imagehash
import matplotlib.pyplot as plt
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, confusion_matrix
print("TensorFlow", tf.__version__, "| Keras", keras.__version__)
""")

code(r"""
# ---- Configuration -------------------------------------------------------
MODEL_NAME  = "orora_droppings_v1"
SEED        = 42
IMG_SIZE    = 224          # model input; the app must resize the same way (whole image, squashed, RGB 0-255)
CACHE_EDGE  = 320          # longest edge of cached copies (keeps the Drive cache small)
BATCH       = 32
EPOCHS_HEAD = 8            # phase 1: frozen backbone
EPOCHS_FT   = 12           # phase 2: fine-tune top of backbone
FT_LAYERS   = 40           # how many backbone layers to unfreeze in phase 2
DEDUP_HAMMING = 4          # perceptual-hash distance counted as "same photo"
USE_DRIVE   = True         # cache resized images and save outputs to Google Drive
SUBSET_PER_CLASS = None    # e.g. 300 for a fast dry run; None = all images

# Model output order. Never reorder after export: the app reads it from labels.json.
CLASSES = ["healthy", "cocci", "salmo", "ncd", "other"]
LABELS  = {"healthy": "Healthy", "cocci": "Coccidiosis", "salmo": "Salmonellosis",
           "ncd": "Newcastle disease", "other": "Not droppings"}
DISEASE = CLASSES[:4]      # the four droppings classes

# "Not droppings" images: (TFDS dataset, split, how many)
OTHER_SOURCES = [  # (name, direct download, how many)
    ("imagenette", "https://s3.amazonaws.com/fast-ai-imageclas/imagenette2-160.tgz", 800),       # everyday objects, ~95 MB
    ("dtd", "https://www.robots.ox.ac.uk/~vgg/data/dtd/download/dtd-r1.0.1.tar.gz", 600),        # textures: soil, cloth, wood, ~600 MB
]

SOURCES = {
  # source -> {class: Zenodo download URL}
  "v2": {  # farm-labelled, training source
    "cocci":   "https://zenodo.org/api/records/4628934/files/cocci.zip/content",
    "healthy": "https://zenodo.org/api/records/4628934/files/healthy.zip/content",
    "salmo":   "https://zenodo.org/api/records/4628934/files/salmo.zip/content",
    "ncd":     "https://zenodo.org/api/records/4628934/files/ncd.zip/content",
  },
  "pcr": {  # PCR-confirmed, evaluation only
    "cocci":   "https://zenodo.org/api/records/5801834/files/pcrcocci.zip/content",
    "healthy": "https://zenodo.org/api/records/5801834/files/pcrhealthy.zip/content",
    "salmo":   "https://zenodo.org/api/records/5801834/files/pcrsalmo.zip/content",
    "ncd":     "https://zenodo.org/api/records/5801834/files/pcrncd.zip/content",
  },
}

random.seed(SEED); np.random.seed(SEED); tf.random.set_seed(SEED)

# Orora brand palette for charts
TEAL, MIDTEAL, SAGE, ORANGE, GREY = "#1F5E5C", "#3E8E8B", "#8FB9B5", "#E97132", "#5A5A5A"
""")

code(r"""
# ---- Where things live ---------------------------------------------------
# DRIVE_MODE: "mount" = Drive as a folder (normal); "api" = fallback when mounting fails:
# files are fetched from / sent to Drive through the Drive API instead; None = no Drive.
DRIVE_MODE = None
DRIVE_FOLDER = ["Orora AgriTech", "baseline"]
if USE_DRIVE:
    from google.colab import drive
    try:
        drive.mount("/content/drive", force_remount=True)
        DRIVE_MODE = "mount"
    except Exception as e:
        print(f"Drive mount failed ({e}). Switching to the Drive API fallback.")
        from google.colab import auth
        auth.authenticate_user()          # a different sign-in pop-up: allow it
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
        gdrive = build("drive", "v3")
        DRIVE_MODE = "api"

def drive_folder_id(create=False):
    parent = "root"
    for name in DRIVE_FOLDER:
        q = (f"name = '{name}' and '{parent}' in parents and trashed = false "
             "and mimeType = 'application/vnd.google-apps.folder'")
        found = gdrive.files().list(q=q, fields="files(id)").execute()["files"]
        if found:
            parent = found[0]["id"]
        elif create:
            parent = gdrive.files().create(fields="id", body={"name": name, "parents": [parent],
                     "mimeType": "application/vnd.google-apps.folder"}).execute()["id"]
        else:
            return None
    return parent

def drive_get(name, dst):
    fid = drive_folder_id()
    if not fid: return False
    q = f"name = '{name}' and '{fid}' in parents and trashed = false"
    found = gdrive.files().list(q=q, fields="files(id,size)").execute()["files"]
    if not found: return False
    with open(dst, "wb") as fh:
        dl = MediaIoBaseDownload(fh, gdrive.files().get_media(fileId=found[0]["id"]), chunksize=64 << 20)
        done = False
        while not done:
            _, done = dl.next_chunk()
    return True

def drive_put(src):
    fid = drive_folder_id(create=True)
    media = MediaFileUpload(str(src), resumable=True)
    gdrive.files().create(body={"name": pathlib.Path(src).name, "parents": [fid]},
                          media_body=media, fields="id").execute()

OUT = pathlib.Path("/content/drive/MyDrive/Orora AgriTech/baseline") if DRIVE_MODE == "mount" \
      else pathlib.Path("/content/out")
OUT.mkdir(parents=True, exist_ok=True)
RAW   = pathlib.Path("/content/raw")     # zips + unzipped originals (local disk, deleted after caching)
CACHE = pathlib.Path("/content/cache")   # resized copies: cache/<source>/<class>/<file>.jpg
CACHE_TAR = OUT / "cache_resized.tar"    # the Drive copy of CACHE, so re-runs skip the 8 GB download
print("Drive:", DRIVE_MODE, "| outputs ->", OUT)
""")

# --------------------------------------------------------------------------
md(r"""
## 1–3 · Droppings images: download, resize, cache

The first run downloads about 5.8 GB (v2 classes) plus 4.4 GB (PCR set) **onto the Colab machine**. It resizes every image so its longest edge is 320 px and saves a small tar to Drive. Later runs just restore that tar.
""")
code(r"""
IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

def resize_one(src, dst):
    try:
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        im.thumbnail((CACHE_EDGE, CACHE_EDGE), Image.LANCZOS)
        dst.parent.mkdir(parents=True, exist_ok=True)
        im.save(dst, "JPEG", quality=92)
        return True
    except Exception as e:
        print("skip", src, e)
        return False

def build_cache():
    RAW.mkdir(exist_ok=True)
    for source, urls in SOURCES.items():
        for cls, url in urls.items():
            zp = RAW / f"{source}_{cls}.zip"
            ex = RAW / f"{source}_{cls}"
            if not ex.exists():
                print(f"Downloading {source}/{cls} ...")
                subprocess.run(["wget", "-q", "-c", "-O", str(zp), url], check=True)
                subprocess.run(["unzip", "-q", "-o", str(zp), "-d", str(ex)], check=True)
                zp.unlink()
            files = [p for p in ex.rglob("*") if p.suffix.lower() in IMG_EXT and not p.name.startswith(".")]
            jobs = []
            with cf.ThreadPoolExecutor(8) as pool:
                for p in files:
                    # keep the relative path in the name so files from sub-folders never collide
                    name = "__".join(p.relative_to(ex).with_suffix(".jpg").parts)
                    jobs.append(pool.submit(resize_one, p, CACHE / source / cls / name))
            ok = sum(j.result() for j in jobs)
            print(f"  {source}/{cls}: {ok} of {len(files)} images cached")
            shutil.rmtree(ex)   # free local disk
    with tarfile.open(CACHE_TAR, "w") as t:
        t.add(CACHE, arcname="cache")
    if DRIVE_MODE == "api":
        try:
            drive_put(CACHE_TAR)
        except Exception as e:
            print("Could not upload the cache to Google Drive:", e)
    print("Cache saved to", CACHE_TAR)

have_droppings = lambda: (CACHE / "v2").exists() and any((CACHE / "v2").rglob("*.jpg"))
if DRIVE_MODE == "api" and not CACHE_TAR.exists() and not have_droppings():
    print("Fetching the image cache from Google Drive through the API ...")
    print("  found" if drive_get(CACHE_TAR.name, CACHE_TAR) else "  not found in Drive")

if have_droppings():
    print("Cache already on local disk.")
elif CACHE_TAR.exists():
    print("Restoring cache from Drive ...")
    with tarfile.open(CACHE_TAR) as t:
        t.extractall("/content")
else:
    t0 = time.time(); build_cache(); print(f"Done in {(time.time()-t0)/60:.1f} min")
""")

md(r"""
## 3b · "Not droppings" images

Everyday objects and scenes (Imagenette) and surface textures such as soil, cloth, wood and stone (DTD). Textures matter most: they look like the ground around droppings but contain none. Any photos in Drive under `Orora AgriTech/other_training/` are added on top. These are Orora's own negatives, and they are the ones that will matter in the field.
""")
code(r"""
# Direct downloads (tensorflow_datasets is broken on current Colab: protobuf version clash)
OTHER_DIR = CACHE / "other" / "other"

def take_images(root, n, prefix):
    files = sorted(p for p in pathlib.Path(root).rglob("*") if p.suffix.lower() in IMG_EXT)
    random.Random(SEED).shuffle(files)
    k = 0
    for p in files:
        if k >= n:
            break
        if resize_one(p, OTHER_DIR / f"{prefix}_{k:04d}.jpg"):
            k += 1
    return k

if OTHER_DIR.exists() and any(OTHER_DIR.glob("*.jpg")):
    print("'Not droppings' images already on local disk:", len(list(OTHER_DIR.glob("*.jpg"))))
else:
    RAW.mkdir(exist_ok=True)
    for name, url, n in OTHER_SOURCES:
        try:
            tgz = RAW / f"{name}.tgz"
            subprocess.run(["wget", "-q", "-c", "-O", str(tgz), url], check=True)
            dst = RAW / name
            dst.mkdir(exist_ok=True)
            subprocess.run(["tar", "-xzf", str(tgz), "-C", str(dst)], check=True)
            print(f"  {name}: {take_images(dst, n, name)} images")
            shutil.rmtree(dst); tgz.unlink()
        except Exception as e:   # one source failing must not stop the run
            print(f"  {name}: skipped ({e})")

    own = OUT.parent / "other_training"
    if own.exists():
        print(f"  Orora's own 'other' photos: {take_images(own, 10_000, 'orora')}")

n_other = len(list(OTHER_DIR.glob("*.jpg")))
print("'Not droppings' images:", n_other)
assert n_other >= 200, "Too few 'not droppings' images: check the messages above."
""")

code(r"""
rows = [{"path": str(p), "source": p.parts[-3], "cls": p.parts[-2]}
        for p in CACHE.rglob("*.jpg")]
df = pd.DataFrame(rows)
print(df.groupby(["source", "cls"]).size().unstack(0).reindex(CLASSES))

fig, axes = plt.subplots(len(CLASSES), 5, figsize=(12, 12))
for r, c in enumerate(CLASSES):
    src = "other" if c == "other" else "v2"
    sample = df[(df.source == src) & (df.cls == c)].sample(5, random_state=SEED)
    for k, p in enumerate(sample.path):
        axes[r, k].imshow(Image.open(p)); axes[r, k].axis("off")
    axes[r, 0].set_title(LABELS[c], loc="left", color=TEAL, fontsize=11)
plt.tight_layout(); plt.show()
""")

# --------------------------------------------------------------------------
md(r"""
## 4 · Duplicate check between v2 and the PCR set

v2 and v3 come from the same study, so some photos may appear in both. A photo seen in training would make the PCR test look better than it is. Any v2 image within a small perceptual-hash distance of a PCR image is **removed from training**.
""")
code(r"""
def phash(p):
    try:
        return imagehash.phash(Image.open(p))
    except Exception:
        return None

with cf.ThreadPoolExecutor(8) as pool:
    df["hash"] = list(pool.map(phash, df.path))
df = df[df.hash.notna()].reset_index(drop=True)

pcr   = df[df.source == "pcr"]
v2    = df[df.source == "v2"].copy()
other = df[df.source == "other"].drop_duplicates("hash").copy()

# compare as 64-bit integers: Hamming distance = popcount(xor)
to_int = lambda h: int(str(h), 16)
pcr_bits = np.array([to_int(h) for h in pcr.hash], dtype=np.uint64)
v2_bits  = np.array([to_int(h) for h in v2.hash],  dtype=np.uint64)

def min_hamming(x, arr, chunk=4096):
    best = 64
    for i in range(0, len(arr), chunk):
        xor = np.bitwise_xor(arr[i:i+chunk], np.uint64(x))
        d = np.unpackbits(xor.view(np.uint8).reshape(-1, 8), axis=1).sum(1).min()
        best = min(best, int(d))
    return best

v2["dist_to_pcr"] = [min_hamming(b, pcr_bits) for b in v2_bits]
dups = v2[v2.dist_to_pcr <= DEDUP_HAMMING]
print(f"v2 images that match a PCR image: {len(dups)} (removed from training)")
print(dups.groupby("cls").size().reindex(DISEASE, fill_value=0))
v2 = v2[v2.dist_to_pcr > DEDUP_HAMMING].reset_index(drop=True)

# also drop exact duplicates inside v2 so they cannot straddle train and test
before = len(v2); v2 = v2.drop_duplicates("hash").reset_index(drop=True)
print(f"exact duplicates inside v2 removed: {before - len(v2)}")

# Near-duplicates inside v2 (the same pile photographed twice) are GROUPED, not removed:
# a group always lands entirely in train, or val, or test, so the test set is honest.
bits = np.array([to_int(h) for h in v2.hash], dtype=np.uint64)
popcount = getattr(np, "bitwise_count", None) or (
    lambda a: np.unpackbits(a.view(np.uint8).reshape(-1, 8), axis=1).sum(1))
parent = list(range(len(bits)))
def find(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]; i = parent[i]
    return i
for i in range(len(bits)):
    near = np.nonzero(popcount(np.bitwise_xor(bits[i + 1:], bits[i])) <= DEDUP_HAMMING)[0] + i + 1
    for j in near:
        ri, rj = find(i), find(int(j))
        if ri != rj: parent[rj] = ri
v2["group"] = [find(i) for i in range(len(bits))]
sizes = v2.group.value_counts()
print(f"near-duplicate groups: {int((sizes > 1).sum())} groups covering {int(sizes[sizes > 1].sum())} images")

# "Not droppings" images join the pool, each in its own group
other["group"] = -1 - np.arange(len(other))
pool_df = pd.concat([v2, other], ignore_index=True)
""")

# --------------------------------------------------------------------------
md("## 5 · Train / validation / test split (≈70 / 15 / 15, stratified, near-duplicates kept together)")
code(r"""
from sklearn.model_selection import StratifiedGroupKFold

if SUBSET_PER_CLASS:
    pool_df = pool_df.groupby("cls", group_keys=False).apply(
        lambda g: g.sample(min(len(g), SUBSET_PER_CLASS), random_state=SEED))

def group_split(d, n_splits):
    # one fold (≈1/n_splits) out, keeping every near-duplicate group on one side
    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=SEED)
    keep, out = next(sgkf.split(d, d.cls, groups=d.group))
    return d.iloc[keep], d.iloc[out]

rest, test_df = group_split(pool_df, 7)   # ≈15% test
train_df, val_df = group_split(rest, 6)   # ≈15% of the total for validation
assert not set(train_df.group) & set(test_df.group), "near-duplicate leak between train and test"
pcr_df = pcr.copy()

for name, d in [("train", train_df), ("val", val_df), ("test", test_df), ("pcr", pcr_df)]:
    print(f"{name:5s}", d.cls.value_counts().reindex(CLASSES, fill_value=0).to_dict())

cls_idx = {c: i for i, c in enumerate(CLASSES)}
weights = compute_class_weight("balanced", classes=np.arange(len(CLASSES)),
                               y=train_df.cls.map(cls_idx).values)
CLASS_WEIGHT = dict(enumerate(weights))
print("class weights:", {CLASSES[k]: round(float(v), 2) for k, v in CLASS_WEIGHT.items()})

pd.concat([train_df.assign(split="train"), val_df.assign(split="val"),
           test_df.assign(split="test")])[["path", "cls", "split"]].to_csv(OUT / "split.csv", index=False)
""")

code(r"""
AUTOTUNE = tf.data.AUTOTUNE

def load(path, label):
    img = tf.io.decode_jpeg(tf.io.read_file(path), channels=3)
    img = tf.image.resize(img, (IMG_SIZE, IMG_SIZE))        # squash whole image, as the app will
    return tf.cast(img, tf.float32), label                   # 0-255; the model rescales internally

augment = keras.Sequential([
    keras.layers.RandomFlip("horizontal_and_vertical"),
    keras.layers.RandomRotation(0.15),
    keras.layers.RandomZoom(0.15),
    keras.layers.RandomBrightness(0.2, value_range=(0, 255)),
    keras.layers.RandomContrast(0.2),
], name="augment")

def make_ds(d, training=False):
    ds = tf.data.Dataset.from_tensor_slices((d.path.values, d.cls.map(cls_idx).values))
    if training:
        ds = ds.shuffle(len(d), seed=SEED, reshuffle_each_iteration=True)
    ds = ds.map(load, num_parallel_calls=AUTOTUNE)
    if training:
        ds = ds.map(lambda x, y: (tf.clip_by_value(augment(x, training=True), 0, 255), y),
                    num_parallel_calls=AUTOTUNE)
    return ds.batch(BATCH).prefetch(AUTOTUNE)

train_ds, val_ds = make_ds(train_df, True), make_ds(val_df)
test_ds, pcr_ds  = make_ds(test_df), make_ds(pcr_df)
""")

# --------------------------------------------------------------------------
md(r"""
## 6–7 · Model and training

The backbone is **MobileNetV3-Small**, pre-trained on ImageNet, which makes a model of about 1–2 MB. It includes its own input rescaling, so it takes raw 0–255 RGB. Training runs in two phases:
1. Train only a new classification head, with the backbone frozen.
2. Unfreeze the top backbone layers and fine-tune them at a low learning rate.

Class weights compensate for the small Newcastle class.
""")
code(r"""
base = keras.applications.MobileNetV3Small(
    input_shape=(IMG_SIZE, IMG_SIZE, 3), include_top=False, weights="imagenet",
    include_preprocessing=True, pooling="avg")
base.trainable = False

inputs  = keras.Input((IMG_SIZE, IMG_SIZE, 3), name="image")
x       = base(inputs, training=False)
x       = keras.layers.Dropout(0.3)(x)
outputs = keras.layers.Dense(len(CLASSES), activation="softmax", name="probs")(x)
model   = keras.Model(inputs, outputs, name=MODEL_NAME)

def fit(epochs, lr, tag):
    model.compile(optimizer=keras.optimizers.Adam(lr),
                  loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    ckpt = OUT / f"best_{tag}.keras"
    return model.fit(train_ds, validation_data=val_ds, epochs=epochs, class_weight=CLASS_WEIGHT,
        callbacks=[keras.callbacks.EarlyStopping("val_loss", patience=4, restore_best_weights=True),
                   keras.callbacks.ModelCheckpoint(ckpt, monitor="val_loss", save_best_only=True)])

h1 = fit(EPOCHS_HEAD, 1e-3, "head")
""")
code(r"""
base.trainable = True
for layer in base.layers[:-FT_LAYERS]:
    layer.trainable = False
for layer in base.layers:                      # keep BatchNorm statistics frozen while fine-tuning
    if isinstance(layer, keras.layers.BatchNormalization):
        layer.trainable = False

h2 = fit(EPOCHS_FT, 1e-5, "ft")
model.save(OUT / f"{MODEL_NAME}.keras")

hist = {k: h1.history[k] + h2.history[k] for k in ["accuracy", "val_accuracy", "loss", "val_loss"]}
fig, ax = plt.subplots(1, 2, figsize=(11, 3.5))
for a, m in zip(ax, ["accuracy", "loss"]):
    a.plot(hist[m], color=TEAL, label="train"); a.plot(hist["val_" + m], color=ORANGE, label="validation")
    a.axvline(len(h1.history["loss"]) - 0.5, color=GREY, ls=":", lw=1)
    a.set_title(m); a.legend(frameon=False); a.spines[["top", "right"]].set_visible(False)
plt.show()
""")

# --------------------------------------------------------------------------
md(r"""
## 8 · Evaluation: per class, on two test sets

- **Held-out test**: images never trained on, labelled the same way as the training data. Includes "not droppings" images.
- **PCR set**: droppings whose labels a laboratory confirmed, with any image overlapping the training data removed. This is the stricter test. It has no "not droppings" images.

**Recall** answers: *of the sick birds with this disease, how many did we catch?* That is the number to put on the pitch slide.
""")
code(r"""
IDX = list(range(len(CLASSES)))
NAMES = [LABELS[c] for c in CLASSES]

def evaluate(ds, d, name):
    probs = model.predict(ds, verbose=0)
    y_true, y_pred = d.cls.map(cls_idx).values, probs.argmax(1)
    rep = classification_report(y_true, y_pred, labels=IDX, target_names=NAMES,
                                digits=3, output_dict=True, zero_division=0)
    print(f"\n=== {name}  (n = {len(d)}) ===")
    print(classification_report(y_true, y_pred, labels=IDX, target_names=NAMES, digits=3, zero_division=0))
    cm = confusion_matrix(y_true, y_pred, labels=IDX)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.imshow(cm, cmap=plt.matplotlib.colors.LinearSegmentedColormap.from_list("t", ["#FFFFFF", TEAL]))
    for i in IDX:
        for j in IDX:
            ax.text(j, i, cm[i, j], ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black")
    ax.set_xticks(IDX, NAMES, rotation=30, ha="right"); ax.set_yticks(IDX, NAMES)
    ax.set_xlabel("predicted"); ax.set_ylabel("true"); ax.set_title(name, color=TEAL, loc="left")
    plt.tight_layout(); plt.show()
    return rep, probs

rep_test, p_test = evaluate(test_ds, test_df, "Held-out test")
rep_pcr,  _      = evaluate(pcr_ds,  pcr_df,  "PCR-confirmed set")

# The guard: what happens to photos that are not droppings, and to droppings photos
y_test = test_df.cls.map(cls_idx).values
pred = p_test.argmax(1)
is_other, other_i = (y_test == cls_idx["other"]), cls_idx["other"]
guard = {
    "not_droppings_refused": float((pred[is_other] == other_i).mean()),
    "not_droppings_called_healthy": float((pred[is_other] == cls_idx["healthy"]).mean()),
    "droppings_wrongly_refused": float((pred[~is_other] == other_i).mean()),
}
print(f"Not-droppings photos refused: {guard['not_droppings_refused']:.1%} "
      f"| called 'healthy': {guard['not_droppings_called_healthy']:.1%} "
      f"| real droppings wrongly refused: {guard['droppings_wrongly_refused']:.1%}")

metrics = {"model": MODEL_NAME, "backbone": "MobileNetV3Small", "img_size": IMG_SIZE, "classes": CLASSES,
           "train_n": len(train_df), "val_n": len(val_df), "test_n": len(test_df),
           "test": rep_test, "pcr": rep_pcr, "guard": guard,
           "dedup_removed_from_train": int(len(dups)),
           "data": ["Machuve et al., Zenodo 10.5281/zenodo.4628934 (CC BY 4.0)",
                    "Machuve et al., Zenodo 10.5281/zenodo.5801834 (CC BY 4.0)",
                    "Imagenette (fast.ai) and DTD (Cimpoi et al.): research use, 'not droppings' class"]}
json.dump(metrics, open(OUT / "metrics.json", "w"), indent=2)

slide = pd.DataFrame({
    "Condition": NAMES + ["Overall accuracy"],
    "Held-out test": [f"{rep_test[n]['recall']:.0%}" for n in NAMES] + [f"{rep_test['accuracy']:.0%}"],
    "PCR set": [f"{rep_pcr[n]['recall']:.0%}" if rep_pcr[n]["support"] else "n/a" for n in NAMES]
               + [f"{rep_pcr['accuracy']:.0%}"]})
print("\nFor the Results slide (share of cases caught):"); print(slide.to_string(index=False))
""")

md(r"""
### Confidence threshold for the app

The app should say *"unclear, retake the photo or call the vet"* rather than guess. The table below shows, for each confidence threshold on the validation set, how many photos the app would answer and how accurate those answers are. Pick a threshold and put it in `labels.json`.
""")
code(r"""
vp = model.predict(val_ds, verbose=0); vy = val_df.cls.map(cls_idx).values
rows = []
for t in [0.0, 0.5, 0.6, 0.7, 0.8, 0.9]:
    keep = vp.max(1) >= t
    rows.append({"threshold": t, "answered": f"{keep.mean():.0%}",
                 "accuracy when answered": f"{(vp.argmax(1)[keep] == vy[keep]).mean():.1%}" if keep.any() else "-"})
print(pd.DataFrame(rows).to_string(index=False))
CONF_THRESHOLD = 0.7   # <- adjust after reading the table
""")

# --------------------------------------------------------------------------
md(r"""
## 9–10 · Export for the web app and phones

- **`orora_droppings_v1_fp16.tflite`**: the file the web app runs in the browser (TFLite WebAssembly runtime).
- **`orora_droppings_v1_int8.tflite`**: fully int8-quantised, the smallest; for a native Android app or a microcontroller.

Each exported model is checked against the Keras model on the test set: how often do they agree, and how accurate is each?
""")
code(r"""
SAVED = OUT / "saved_model"
model.export(str(SAVED))          # Keras 3: SavedModel for serving/conversion

def rep_data():
    for p in train_df.sample(300, random_state=SEED).path:
        img, _ = load(p, 0)
        yield [tf.expand_dims(img, 0)]

conv = tf.lite.TFLiteConverter.from_saved_model(str(SAVED))
conv.optimizations = [tf.lite.Optimize.DEFAULT]
conv.representative_dataset = rep_data
conv.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
conv.inference_input_type = tf.uint8
conv.inference_output_type = tf.uint8
int8_path = OUT / f"{MODEL_NAME}_int8.tflite"
int8_path.write_bytes(conv.convert())

conv = tf.lite.TFLiteConverter.from_saved_model(str(SAVED))
conv.optimizations = [tf.lite.Optimize.DEFAULT]
conv.target_spec.supported_types = [tf.float16]
fp16_path = OUT / f"{MODEL_NAME}_fp16.tflite"
fp16_path.write_bytes(conv.convert())

for p in [int8_path, fp16_path]:
    print(f"{p.name}: {p.stat().st_size/1e6:.2f} MB")
""")
code(r"""
def tflite_predict(path, d):
    # The default XNNPACK delegate cannot prepare some int8 MobileNetV3 ops on the Colab CPU;
    # the plain built-in kernels run everything. (Phones use their own delegates.)
    it = tf.lite.Interpreter(model_path=str(path),
        experimental_op_resolver_type=tf.lite.experimental.OpResolverType.BUILTIN_WITHOUT_DEFAULT_DELEGATES)
    it.allocate_tensors()
    inp, out = it.get_input_details()[0], it.get_output_details()[0]
    preds = []
    for p in d.path:
        img, _ = load(p, 0)
        x = img.numpy()[None]
        if inp["dtype"] == np.uint8:
            s, z = inp["quantization"]; x = np.clip(np.round(x / s + z), 0, 255).astype(np.uint8)
        it.set_tensor(inp["index"], x.astype(inp["dtype"])); it.invoke()
        y = it.get_tensor(out["index"])[0].astype(np.float32)
        if out["dtype"] == np.uint8:
            s, z = out["quantization"]; y = (y - z) * s
        preds.append(y.argmax())
    return np.array(preds)

keras_pred = model.predict(test_ds, verbose=0).argmax(1)
y_true = test_df.cls.map(cls_idx).values
for p in [fp16_path, int8_path]:
    try:
        tp = tflite_predict(p, test_df)
        print(f"{p.name}: agrees with Keras on {(tp == keras_pred).mean():.1%} | "
              f"accuracy {(tp == y_true).mean():.1%} vs Keras {(keras_pred == y_true).mean():.1%}")
    except Exception as e:   # a check, not an export step: never block the cells after it
        print(f"{p.name}: could not be checked here ({e}). The file is still saved.")
""")

code(r"""
# Labels + preprocessing contract for the app. The app must follow this exactly.
json.dump({
    "model": MODEL_NAME,
    "file": fp16_path.name,
    "classes": CLASSES,
    "labels_en": [LABELS[c] for c in CLASSES],
    "reject_class": "other",
    "input": {"size": [IMG_SIZE, IMG_SIZE], "channels": "RGB", "range": "0-255",
              "resize": "whole image, squashed to size (no crop)"},
    "confidence_threshold": CONF_THRESHOLD,
    "note": "Decision support, not diagnosis. Suspected Newcastle disease requires laboratory confirmation and official reporting.",
}, open(OUT / "labels.json", "w"), indent=2)
print(open(OUT / "labels.json").read())
""")

# --------------------------------------------------------------------------
md(r"""
## 11 · Optional: test on Orora's own photos

Put vet-labelled photos in Drive under `Orora AgriTech/orora_photos/<class>/`, with folders named `healthy`, `cocci`, `salmo`, `ncd` (and `other` for non-droppings photos). A score lower than on the Tanzanian test set is expected: the Burundian photos differ in lighting, feed, breeds and phones. That gap is the argument for field validation. Report it as it is.
""")
code(r"""
ORORA = OUT.parent / "orora_photos"
files = [(str(p), p.parent.name) for p in ORORA.rglob("*") if p.suffix.lower() in IMG_EXT and p.parent.name in CLASSES]
if not files:
    print("No Orora photos found at", ORORA)
else:
    # decode_jpeg needs JPEG: pass every photo through the same resize used for the cache
    tmp, rows = pathlib.Path("/content/orora_cache"), []
    for i, (p, c) in enumerate(files):
        dst = tmp / c / f"{i:04d}.jpg"
        if resize_one(pathlib.Path(p), dst):
            rows.append((str(dst), c))
    od = pd.DataFrame(rows, columns=["path", "cls"])
    print(od.cls.value_counts().reindex(CLASSES, fill_value=0))
    rep_orora, _ = evaluate(make_ds(od), od, "Orora photos (Burundi)")
    metrics["orora"] = rep_orora
    json.dump(metrics, open(OUT / "metrics.json", "w"), indent=2)
""")

md(r"""
## 12 · Package the app files

This bundles what the app and the pitch need into one small zip: `app_model.zip`, with `labels.json`, `metrics.json` and both TFLite files. It is saved next to the other outputs and **downloaded to your computer**. Unzip it into `app/model/`.
""")
code(r"""
import zipfile
bundle = OUT / "app_model.zip"
with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as z:
    for p in [OUT / "labels.json", OUT / "metrics.json", fp16_path, int8_path]:
        if p.exists():
            z.write(p, p.name)
print(bundle, f"{bundle.stat().st_size/1e6:.1f} MB")
if DRIVE_MODE == "api":
    try:
        for name in ["app_model.zip", f"{MODEL_NAME}.keras", "split.csv"]:
            if (OUT / name).exists():
                drive_put(OUT / name)
        print("Uploaded to Google Drive: Orora AgriTech/baseline/")
    except Exception as e:   # e.g. Drive storage full: the browser download below still works
        print("Could not upload to Google Drive:", e)
from google.colab import files
files.download(str(bundle))
""")

md(r"""
## Outputs (in Drive: `Orora AgriTech/baseline/`)

| File | Use |
|---|---|
| `app_model.zip` | everything the app needs: unzip into `app/model/` |
| `orora_droppings_v1_fp16.tflite` | the model the web app runs |
| `orora_droppings_v1_int8.tflite` | smallest version, for a native Android app or a microcontroller |
| `labels.json` | class order, preprocessing rules, confidence threshold |
| `metrics.json` | per-class results and the "not droppings" guard, for the README and the Results slide |
| `split.csv` | exact train/val/test split, for reproducibility |
| `orora_droppings_v1.keras`, `saved_model/` | source model for retraining |

**Before the pitch:** put the per-class recall from step 8 into the Results slide, and quote only numbers this notebook produced.
""")

nb = {"cells": CELLS,
      "metadata": {"accelerator": "GPU", "colab": {"provenance": [], "gpuType": "T4"},
                   "kernelspec": {"name": "python3", "display_name": "Python 3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
for i, c in enumerate(nb["cells"]):
    c["id"] = f"c{i:02d}"
out = pathlib.Path(__file__).resolve().parent.parent / "notebooks" / "01_baseline_droppings_classifier.ipynb"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
print("WROTE", out, len(CELLS), "cells")
