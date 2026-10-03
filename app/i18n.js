// Orora AgriTech: interface text and advice.
//
// STATUS: English and French are drafts for the hackathon demo. ALL advice must be
// reviewed and signed off by an Orora veterinarian before any producer uses it.
// Kirundi ("rn") is intentionally empty: it must be written by a native speaker with
// the vet, not machine-translated. Missing Kirundi keys fall back to French and the
// app shows a banner saying so.

export const LEVEL = { healthy: "ok", cocci: "warn", salmo: "warn", ncd: "urgent", other: "unclear", unclear: "unclear" };

export const STRINGS = {
  en: {
    title: "Check your flock",
    lead: "Take a photo of fresh droppings. The check runs on this phone, with no internet needed.",
    batchLabel: "Batch or house number (optional)",
    takePhoto: "Take a photo",
    tip1: "Use fresh droppings, less than a few hours old.",
    tip2: "Good daylight, no flash, droppings filling most of the picture.",
    tip3: "One photo per pile. If birds look sick, call the vet anyway.",
    result: "Result",
    whatToDo: "What to do now",
    sendVet: "Send to Orora vet on WhatsApp",
    sendVetUrgent: "Alert the vet now on WhatsApp",
    sharePhoto: "Share the photo with the vet",
    listen: "Listen in Kirundi",
    stopListen: "Stop",
    sendSms: "Send by SMS (works without internet)",
    another: "Check another photo",
    disclaimer: "This is decision support, not a diagnosis. A veterinarian confirms.",
    smsNote: "WhatsApp needs data: with no connection, the message waits and sends when you are back online. SMS goes through with no internet.",
    records: "Batch records",
    recordsNote: "Every check is saved on this phone. Nothing leaves it unless you send it.",
    exportCsv: "Export records (CSV)",
    noRecords: "No checks yet.",
    tabCheck: "Check",
    tabRecords: "Records",
    credits: "Model trained on data by Machuve et al. (CC BY 4.0)",
    online: "Online", offline: "Offline",
    modelLoading: "Loading the model…",
    modelReady: "Model ready. Works offline.",
    modelMissing: "Model not installed yet: add the exported files to app/model/.",
    analysing: "Checking…",
    confidence: "Confidence",
    mockBanner: "TEST MODE: results are random, not from a model. Do not use for decisions.",
    langFallback: "Kirundi translation in progress: showing French.",
    smsHeader: "Orora AgriTech alert",
    labels: { healthy: "Looks healthy", cocci: "Signs of coccidiosis", salmo: "Signs of salmonellosis", ncd: "Possible Newcastle disease", other: "Not droppings", unclear: "Unclear: photo not conclusive" },
    classNames: { healthy: "Healthy", cocci: "Coccidiosis", salmo: "Salmonellosis", ncd: "Newcastle disease", other: "Not droppings" },
    advice: {
      healthy: [
        "Keep the routine: clean water every day, fresh feed, dry litter.",
        "Keep to the vaccination schedule.",
        "Check again in 2–3 days, or sooner if birds eat less or look weak.",
      ],
      cocci: [
        "Separate birds that look weak or have bloody or watery droppings.",
        "Keep litter dry: remove wet litter and fix leaking drinkers.",
        "Contact the Orora vet today about treatment. Do not guess doses.",
        "Clean feeders and drinkers every day.",
      ],
      salmo: [
        "Separate sick birds from the flock.",
        "Wash hands after handling birds or droppings; this infection can pass to people.",
        "Do not sell or eat eggs or meat from sick birds until the vet advises.",
        "Contact the Orora vet today. Antibiotics only on the vet's instruction.",
      ],
      ncd: [
        "URGENT: call the Orora vet now.",
        "Do not move, sell or give away any birds, and keep visitors out.",
        "Separate sick birds. Do not eat or sell birds that die; the vet will advise on safe disposal.",
        "Newcastle disease must be confirmed by a laboratory and reported. The vet will handle this.",
      ],
      other: [
        "This photo does not look like droppings, so no check was made.",
        "Photograph one pile of fresh droppings, close up, in daylight, filling most of the picture.",
        "If birds look sick (not eating, coughing, sleepy, dying), call the vet anyway.",
      ],
      unclear: [
        "Take another photo: fresh droppings, daylight, close up.",
        "If birds look sick (not eating, coughing, sleepy, dying), call the vet anyway.",
      ],
    },
  },

  fr: {
    title: "Contrôler votre élevage",
    lead: "Prenez une photo de fientes fraîches. L'analyse se fait sur ce téléphone, sans internet.",
    batchLabel: "Numéro de lot ou de poulailler (facultatif)",
    takePhoto: "Prendre une photo",
    tip1: "Utilisez des fientes fraîches, de moins de quelques heures.",
    tip2: "Bonne lumière du jour, sans flash, les fientes remplissant l'image.",
    tip3: "Une photo par tas. Si les volailles semblent malades, appelez quand même le vétérinaire.",
    result: "Résultat",
    whatToDo: "Que faire maintenant",
    sendVet: "Envoyer au vétérinaire Orora sur WhatsApp",
    sendVetUrgent: "Alerter le vétérinaire maintenant sur WhatsApp",
    sharePhoto: "Partager la photo avec le vétérinaire",
    listen: "Écouter en kirundi",
    stopListen: "Arrêter",
    sendSms: "Envoyer par SMS (sans internet)",
    another: "Analyser une autre photo",
    disclaimer: "Il s'agit d'une aide à la décision, pas d'un diagnostic. Un vétérinaire confirme.",
    smsNote: "WhatsApp a besoin de données : sans connexion, le message attend et part dès le retour du réseau. Le SMS passe sans internet.",
    records: "Registre des lots",
    recordsNote: "Chaque contrôle est enregistré sur ce téléphone. Rien n'en sort sans votre accord.",
    exportCsv: "Exporter le registre (CSV)",
    noRecords: "Aucun contrôle pour l'instant.",
    tabCheck: "Contrôle",
    tabRecords: "Registre",
    credits: "Modèle entraîné sur les données de Machuve et al. (CC BY 4.0)",
    online: "En ligne", offline: "Hors ligne",
    modelLoading: "Chargement du modèle…",
    modelReady: "Modèle prêt. Fonctionne hors ligne.",
    modelMissing: "Modèle non installé : ajoutez les fichiers exportés dans app/model/.",
    analysing: "Analyse…",
    confidence: "Confiance",
    mockBanner: "MODE TEST : résultats aléatoires, sans modèle. Ne pas utiliser pour décider.",
    langFallback: "Traduction en kirundi en cours : affichage en français.",
    smsHeader: "Alerte Orora AgriTech",
    labels: { healthy: "Semble en bonne santé", cocci: "Signes de coccidiose", salmo: "Signes de salmonellose", ncd: "Maladie de Newcastle possible", other: "Pas des fientes", unclear: "Incertain : photo non concluante" },
    classNames: { healthy: "Sain", cocci: "Coccidiose", salmo: "Salmonellose", ncd: "Maladie de Newcastle", other: "Pas des fientes" },
    advice: {
      healthy: [
        "Gardez la routine : eau propre chaque jour, aliment frais, litière sèche.",
        "Respectez le calendrier de vaccination.",
        "Contrôlez à nouveau dans 2 à 3 jours, ou plus tôt si les volailles mangent moins ou semblent faibles.",
      ],
      cocci: [
        "Isolez les volailles faibles ou aux fientes sanglantes ou liquides.",
        "Gardez la litière sèche : retirez la litière humide et réparez les abreuvoirs qui fuient.",
        "Contactez aujourd'hui le vétérinaire Orora pour le traitement. Ne devinez pas les doses.",
        "Nettoyez mangeoires et abreuvoirs chaque jour.",
      ],
      salmo: [
        "Isolez les volailles malades du reste du troupeau.",
        "Lavez-vous les mains après avoir touché les volailles ou les fientes : cette infection peut passer à l'homme.",
        "Ne vendez ni ne consommez les œufs ou la viande des volailles malades avant l'avis du vétérinaire.",
        "Contactez aujourd'hui le vétérinaire Orora. Antibiotiques uniquement sur prescription.",
      ],
      ncd: [
        "URGENT : appelez maintenant le vétérinaire Orora.",
        "Ne déplacez, ne vendez et ne donnez aucune volaille, et interdisez les visites.",
        "Isolez les volailles malades. Ne consommez ni ne vendez les volailles mortes ; le vétérinaire indiquera comment les éliminer.",
        "La maladie de Newcastle doit être confirmée par un laboratoire et déclarée. Le vétérinaire s'en charge.",
      ],
      other: [
        "Cette photo ne ressemble pas à des fientes : aucune analyse n'a été faite.",
        "Photographiez un tas de fientes fraîches, de près, à la lumière du jour, remplissant l'image.",
        "Si les volailles semblent malades (ne mangent pas, toussent, sont abattues, meurent), appelez quand même le vétérinaire.",
      ],
      unclear: [
        "Reprenez une photo : fientes fraîches, lumière du jour, de près.",
        "Si les volailles semblent malades (ne mangent pas, toussent, sont abattues, meurent), appelez quand même le vétérinaire.",
      ],
    },
  },

  // Kirundi: to be written by a native speaker with the Orora vet. Empty keys fall back to French.
  rn: /*RN-START*/{
    "sendVet": "Rungikira umuganga w'ibitungwa wa Orora kuri Whatsapp",
    "sendVetUrgent": "Kumenyesha umuganga w'ibiturwa ubunyene kuri Whatsapp",
    "sharePhoto": "Rungikira ishusho ku muganga w'ibitungwa",
    "sendSms": "Rungika ubutumwa (Ntibisaba Interineti)",
    "disclaimer": "bisaba ubufasha kungingo,ata gipimo. vyemezwa n'umuganga w'ibitungwa.",
    "smsNote": "Message isanzwe igenda ubunyene. Whatsapp isaba ko uba uri kumurongo, utari kumurongo ubutumwa buza kugenda usubiye kumurongo.",
    "smsHeader": "Ubutumwa bwa Orora AgriTech",
    "labels": {
      "healthy": "Ntagorane ihari",
      "cocci": "ibimenyetso vya kocidiyoze",
      "salmo": "ibimenyetso vya Saromonera",
      "ncd": "Ibimenetso vy'ingwara y'agahweka",
      "other": "Nta masyenkoko aboneka",
      "unclear": "amakenga: ishusho ntiyoba iyifatiro"
    },
    "classNames": {
      "healthy": "nziza",
      "cocci": "kocidiyoze",
      "salmo": "saromonera",
      "ncd": "indwara y'agahweka",
      "other": "Nta masyenkoko aboneka"
    },
    "advice": {
      "healthy": [
        "Cunga isuku:amazi meza buri umunsi, indya nziza, ibisasizo vy'umutse",
        "kurikiza ikiranga minsi c'incanco",
        "suzuma gushasha mu minsi 2 canke 3, canke imbere yaho, kwa ata nkoko irya nabi canke igoyagoya"
      ],
      "cocci": [
        "shira kuruhande inkoko zigoyagoya canke zita amasyenkoko arimwo amaraso",
        "Gumiza ibisasizo vyumutse:kura ibisasizo vyatose kandi homa ivyozinyeramwo vyatobotse",
        "rondera uyumunsi umuganga w'inkoko kugira ayivure. Ntuhindure urugero kwogutangako umuti.",
        "hanagura ivyo ziriramwo nivyo zinyweramwo kumusi kumusi"
      ],
      "salmo": [
        "kura muzindi inkoko zirwaye",
        "karaba iminwe igihe wakoze ku nkoko canke amase: uwomugera ushobora kujanwa n'umuntu.",
        "ntucuruze canke ufungure amagi canke inyama yinkoko irwaye ataruhusha rwa muganga",
        "hamagara uyu munsi umuganga w'inkoko. antibiyotike itangwa gusa ubibwiwe n'umuganga"
      ],
      "ncd": [
        "ICIHUTIRWA: Hamagara ubu nyene umuganga w'inkoko",
        "ntiwimure, ntudandaze canke ntujane ahandi inkoko n'imwe, kandi ntusubire kwakira ingenzi.",
        "Shira k'uruhande inkoko irwaye. Ntufungure canke ucuruze inkoko zapfuye; umuganga w'ibitungwa azobabwira iyo muzishira",
        "Indwara y'agahweka itegerezwa kwemezwa ninzu y'ubushakashatsi, ikanabitangaza. Ni igikorwa c'umuganga w'ibitungwa."
      ],
      "other": [
        "iyi sanamu ntisa nk'amase y'inkoko: ntawundi mwihwezo wabaye.",
        "Fata isanamu yumurwi w'amase mabisi, egera, kumuco wumutaga, uzuza isanamu.",
        "iyo inkoko zimeze nkizirwaye (ntizirya, zirakorora, zirisinzirirako, zirapfa), hamagara nimiburiburi umuganga w'ibitungwa."
      ],
      "unclear": [
        "subiramwo isanamu: amase mabisi, umuco w'umurango, egera.",
        "iyo inkoko zimeze nkizirwaye (ntizirya, zikorora, zirisinzirirako, zirapfa), hamagara nimiburiburi umuganga w'ibitungwa."
      ]
    },
    "title": "Suzuma inkoko zawe.",
    "lead": "fata isanamu y'amase mabisi. kora ubushakashatsi kuri teretefone udakoresheje interinete",
    "batchLabel": "numero yurunganwe canke inkoko zavukiye rimwe (kuwubishatse)",
    "takePhoto": "fata isanamu",
    "tip1": "koresha amaze amasaha make",
    "tip2": "umuco mwiza wo kumurango, ata farashe, amase yuzure isanamu.",
    "tip3": "isanamu y'ikirundo. iyo inkoko imeze nk'iyirwaye, hamagara n'imiburiburi umuganga w'ibitungwa.",
    "result": "inyishu",
    "whatToDo": "hakorwe iki ubu nyene",
    "another": "iga kuyindi shusho",
    "records": "andika ivyuyo murwi",
    "recordsNote": "icowaravye neza cose kiguma muri terefone yawe. ntagisohoka utacemereye.",
    "exportCsv": "imura ivyo wakoze",
    "noRecords": "ntamwihwezo urakorwa",
    "tabCheck": "umwihwezo",
    "tabRecords": "Imura ivyo wanditse",
    "online": "Uri kumurongo",
    "offline": "Nturi kumurongo",
    "modelReady": "Urashobora gukora ubushakashatsi utari kumurongo",
    "analysing": "Umwihwezo",
    "confidence": "umwizero",
    "credits": "Ubushakashatsi bwakozwe na Machuve et al.(CC BY4.0)",
    "modelLoading": "Rindira",
    "modelMissing": "Hari ibikibura:ongerako amafishe yasohowe muri app/mode/.",
    "mockBanner": "GERAGEZA:Ninyishu mfatakibanza, atafatiro zifise. Ntuyikoreshe mugufata ingingo.",
    "langFallback": "ihindurwa mu kirundi birabandanya: twerekana igifaransa"
  }/*RN-END*/,
};

// Look up a key for a language, falling back to French for Kirundi, then English.
export function t(lang, key) {
  const chain = lang === "rn" ? ["rn", "fr", "en"] : [lang, "en"];
  for (const l of chain) {
    const v = STRINGS[l] && STRINGS[l][key];
    if (v !== undefined) return v;
  }
  return key;
}

export const hasFullTranslation = lang =>
  Object.keys(STRINGS.en).every(k => STRINGS[lang] && STRINGS[lang][k] !== undefined);
