# Model files

The app runs `orora_droppings_v0_fp16.tflite` directly in the browser with the TFLite WebAssembly runtime (`@tensorflow/tfjs-tflite`). No TF.js conversion is needed.

| File | Use |
|---|---|
| `orora_droppings_v0_fp16.tflite` | the model the app loads (1.9 MB) |
| `orora_droppings_v0_int8.tflite` | smaller (1.2 MB), for a native Android app or a microcontroller; not used by the web app |
| `labels.json` | class order, input rules, confidence threshold |
| `metrics.json` | per-class results from the notebook |

To update: run `notebooks/01_baseline_droppings_classifier.ipynb`, unzip `app_model.zip` here, then change `VERSION` in `app/sw.js` so installed phones fetch the new model.
