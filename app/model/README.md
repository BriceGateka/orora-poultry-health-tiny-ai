# Model files

The app runs the `.tflite` file named in `labels.json` (key `file`) directly in the browser with the TFLite WebAssembly runtime (`@tensorflow/tfjs-tflite`). If `labels.json` names no file, it falls back to `orora_droppings_v0_fp16.tflite`.

| File | Use |
|---|---|
| `orora_droppings_v*_fp16.tflite` | the model the app loads (about 1.9 MB) |
| `orora_droppings_v*_int8.tflite` | smaller (about 1.2 MB), for a native Android app or a microcontroller; not used by the web app |
| `labels.json` | model file, class order, input rules, confidence threshold |
| `metrics.json` | per-class results from the notebook |

To update: run `notebooks/01_baseline_droppings_classifier.ipynb`, unzip `app_model.zip` here, then change `VERSION` in `app/sw.js` so installed phones fetch the new model.

Deployed: model v1 (5 classes, with "not droppings"). Model v0 (4 classes) is kept for comparison; labels.json decides which file the app loads.
