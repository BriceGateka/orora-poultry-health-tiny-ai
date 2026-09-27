// Orora AgriTech — demo configuration. Edit these before the demo.
export const CONFIG = {
  // Orora vet who receives alerts. SMS works over the mobile network with no internet.
  vetPhone: "+25700000000",            // TODO: real Orora vet number
  vetName: "Orora vet",

  // Model exported by notebooks/01_baseline_droppings_classifier.ipynb (step 9–10):
  // copy Drive "Orora AgriTech/baseline/tfjs/*" into app/model/ and labels.json into app/model/labels.json
  modelUrl: "model/model.json",
  labelsUrl: "model/labels.json",

  // Used only if labels.json is missing. The notebook writes the threshold it chose.
  defaultThreshold: 0.7,
  defaultClasses: ["healthy", "cocci", "salmo", "ncd"],
  defaultSize: 224,
};
