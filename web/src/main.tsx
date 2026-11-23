import {createRoot} from 'react-dom/client';
import App from './App.tsx';
import './index.css';
import './blue-shift.css';
import './cinematic-menu.css';
import './module-scenes-v2.css';
import './module-polish-v3.css';
import './experience-v4.css';
import './experience-v5.css';
import './experience-v6.css';
import './experience-v7-contrast.css';
import './production-v8.css';
import './os-resource-monitor.css';
import './kernel-bridge-v10.css';
import './v11-reload.css';
import './v12-finish.css'; // AUTOOS_V12_APLICADO
import './v14-blackbox.css'; // AUTOOS_V14_BLACKBOX_CLOUD
import './v15-final.css'; // AUTOOS_V15_APLICADO
import './v16-mission.css'; // AUTOOS_V16_ESCENA_JUGABLE
import './v17-final.css'; // AUTOOS_V17_BIFURCACIONES
import './v18-polish.css'; // AUTOOS_V18_PULIDO_VISUAL
import './v19-minigame.css'; // AUTOOS_V19_MINIJUEGO
import './v20-conduccion.css'; // AUTOOS_V20_CRUCES_SIN_PAUSA
import './v21-conduccion.css'; // AUTOOS_V21_MENOS_CRUCES
import { startStreamlitAutoResize } from './utils/iframeResize';

createRoot(document.getElementById('root')!).render(<App />);

// AUTOOS_MODULE_SCENE_V2: el iframe cambia de altura al cambiar de módulo.
startStreamlitAutoResize();
