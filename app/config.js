// Orora AgriTech — demo configuration. Edit these before the demo.
export const CONFIG = {
  // Orora vet who receives alerts. SMS works over the mobile network with no internet.
  vetPhone: "+25700000000",            // TODO: real Orora vet number
  vetName: "Orora vet",

  // Model exported by notebooks/01_baseline_droppings_classifier.ipynb: unzip app_model.zip into app/model/.
  // A .tflite file runs through TFLite-in-the-browser (WebAssembly); a model.json runs as a TF.js graph model.
  modelUrl: "model/orora_droppings_v0_fp16.tflite",
  labelsUrl: "model/labels.json",
  tfliteWasm: "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-tflite@0.0.1-alpha.10/wasm/",

  // Used only if labels.json is missing. The notebook writes the threshold it chose.
  defaultThreshold: 0.7,
  defaultClasses: ["healthy", "cocci", "salmo", "ncd"],
  defaultSize: 224,
};
