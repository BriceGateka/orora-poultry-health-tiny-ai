# Orora AgriTech: offline demo app

Take a photo of chicken droppings; the model runs **on the phone** and returns a result, advice, a one-tap SMS to the Orora vet, and a saved batch record. A photo that is not droppings gets "Not droppings" and no diagnosis. After the first visit it works with **no internet** (service worker + cached model). SMS goes over the mobile network, not data.

## Files
| File | What |
|---|---|
| `index.html`, `styles.css`, `app.js` | the app |
| `config.js` | **set the vet's phone number here** |
| `i18n.js` | interface text and advice (EN, FR; Kirundi to be written) |
| `sw.js` | offline cache: bump `VERSION` after any change |
| `model/` | unzip the notebook's `app_model.zip` here; `labels.json` names the model file to load (see `model/README.md`) |

## Run locally
```
python -m http.server 8765 --directory app
```
Open http://localhost:8765, or http://localhost:8765/?mock=1 for **test mode** (random results, red banner). Test mode is for trying the screens only, never for the demo itself.

## Put it on a phone
Phones need **HTTPS** for the camera, offline mode and "Add to home screen". Easiest options:
- **Netlify Drop:** drag the `app` folder onto app.netlify.com/drop and get an https link.
- **GitHub Pages:** push the repo and serve the `app` folder.

On the phone: open the link once with data on, wait for "Model ready", then *Add to home screen*. Test in airplane mode before the demo.

## Before any real use
- An Orora vet must review and sign off every advice line in `i18n.js`.
- Kirundi must be written by a native speaker with the vet (the app falls back to French and says so).
- The app is decision support, not diagnosis; suspected Newcastle disease requires laboratory confirmation and official reporting.

Model trained on: Machuve et al., *Machine Learning Dataset for Poultry Diseases Diagnostics*, Zenodo (CC BY 4.0).
