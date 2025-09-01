import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { setLanguage } from '../lib/i18n';
type UiState={ locale:'ru'|'en'; setLocale:(l:'ru'|'en')=>void };
export const useUi=create<UiState>()(persist((set)=>({ locale:(localStorage.getItem('oppo-lang') as 'ru'|'en')||'ru', setLocale:(l)=>{ set({locale:l}); setLanguage(l);} }),{name:'oppo-ui'}));
