# Orora Poultry Health: Tiny AI

Offline early warning for poultry disease, built for smallholder producers in Burundi who have no vet nearby and no reliable connectivity. A phone photo of fresh droppings is classified **on the device** (healthy, coccidiosis, salmonellosis, Newcastle disease, or "not droppings" when the photo shows something else); the app gives plain-language advice and sends the case to an Orora veterinarian by SMS.

Built by **Orora Agro Group** (Bujumbura, Burundi) for the Hack-Nation 7th Global AI Hackathon, 3–4 October 2026.

> **Decision support, not diagnosis.** A veterinarian confirms every case. Suspected Newcastle disease requires laboratory confirmation and official reporting.

## Repository
| Path | What |
|---|---|
| `notebooks/01_baseline_droppings_classifier.ipynb` | Colab notebook: data download, MobileNetV3-Small training, per-class evaluation (incl. PCR-confirmed test set and the "not droppings" guard), TFLite fp16 / int8 export, `app_model.zip` |
| `_build/make_notebook.py` | Generates the notebook from plain Python (edit here, then regenerate) |
| `app/` | Offline web app (PWA): camera → on-device model → advice → SMS to vet → batch records. See `app/README.md` |

## Quick start
1. Open the notebook in Google Colab (T4 GPU) and run all cells. Outputs go to Google Drive `Orora AgriTech/baseline/`, and `app_model.zip` downloads to your computer.
2. Unzip `app_model.zip` into `app/model/`.
3. `python -m http.server 8765 --directory app` and open http://localhost:8765 (`?mock=1` = test mode, random results).

## Data and credits
- Machuve D., Nwankwo E., Lyimo E., Maguo E., Munisi C.: *Machine Learning Dataset for Poultry Diseases Diagnostics*, Zenodo, [10.5281/zenodo.4628934](https://doi.org/10.5281/zenodo.4628934) (training) and PCR-annotated version [10.5281/zenodo.5801834](https://doi.org/10.5281/zenodo.5801834) (evaluation only). CC BY 4.0.
- "Not droppings" class: Imagenette (fast.ai, a subset of ImageNet) and the Describable Textures Dataset (Cimpoi et al., Oxford). Research use only; to be replaced by Orora's own photos before commercial use.
- Aworinde et al.: *Poultry Vocalization Signal Dataset for Early Disease Detection*, Mendeley Data, [10.17632/zp4nf2dxbh.1](https://doi.org/10.17632/zp4nf2dxbh.1). CC BY 4.0 (phase 2, sound).

## Rights
© 2026 Orora Agro Group. All rights reserved. Third-party components remain under their own licences.
