# Model files go here

After running `notebooks/01_baseline_droppings_classifier.ipynb`, copy these files from Google Drive (`Orora AgriTech/baseline/`) into this folder:

- `tfjs/model.json` → `app/model/model.json`
- `tfjs/group1-shard*.bin` → `app/model/`
- `labels.json` → `app/model/labels.json`

Then change `VERSION` in `app/sw.js` so phones that already installed the app download the new model.
