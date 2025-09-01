import i18n from "i18next";
import { initReactI18next } from "react-i18next";

const resources = {
  ru: { translation: { "app.title": "Платформа OPPO KZ", "menu.directories": "Справочники", "menu.upload": "Загрузка", "menu.recon": "Сверка" } },
  en: { translation: { "app.title": "OPPO KZ Platform", "menu.directories": "Directories", "menu.upload": "Upload", "menu.recon": "Reconciliation" } }
};

i18n.use(initReactI18next).init({
  resources,
  lng: "ru",
  fallbackLng: "en",
  interpolation: { escapeValue: false }
});

export default i18n;
