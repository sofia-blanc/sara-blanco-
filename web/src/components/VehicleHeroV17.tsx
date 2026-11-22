/**
 * AUTOOS V18 · ilustración vectorial para la portada.
 *
 * Sustituye el asset rasterizado por un dibujo integrado al lenguaje visual
 * del proyecto, para que no se perciba como un PNG pegado.
 */
import React from 'react';

function PreviewVehicle() {
  return <svg viewBox="0 0 560 280" className="v18-hero__svg" aria-hidden="true">
    <defs>
      <linearGradient id="v18heroBody" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#5ff0ff"/><stop offset=".55" stopColor="#2092df"/><stop offset="1" stopColor="#0c3ea0"/></linearGradient>
    </defs>
    <rect x="0" y="0" width="560" height="280" rx="10" fill="#071d4f"/>
    <path d="M43 211H517" stroke="#2a4f8d" strokeWidth="3"/>
    <ellipse cx="280" cy="225" rx="160" ry="18" fill="#021126" opacity=".55"/>
    <path d="M163 175Q196 121 236 109Q278 95 344 101Q390 108 418 154L442 177 450 192Q281 205 114 192L121 176Z"
      fill="url(#v18heroBody)" stroke="#a6f5ff" strokeWidth="4"/>
    <path d="M228 119Q279 87 343 95Q384 100 405 132L419 170H186L198 141Q208 127 228 119Z" fill="#092342" stroke="#90ebff" strokeWidth="4"/>
    <path d="M292 95V169" stroke="#b6fbff" strokeWidth="6"/>
    <path d="M215 171H414" stroke="#c8fcff" strokeWidth="4" opacity=".75"/>
    <circle cx="220" cy="194" r="31" fill="#092244" stroke="#8befff" strokeWidth="5"/>
    <circle cx="393" cy="194" r="31" fill="#092244" stroke="#8befff" strokeWidth="5"/>
    <circle cx="220" cy="194" r="15" fill="#5de6ff"/>
    <circle cx="393" cy="194" r="15" fill="#5de6ff"/>
    <path d="M165 177H130" stroke="#ff5ea2" strokeWidth="14" strokeLinecap="round"/>
    <path d="M447 177H476" stroke="#ff5ea2" strokeWidth="14" strokeLinecap="round"/>
    <path d="M291 84Q342 61 423 79" fill="none" stroke="#67eeff" strokeDasharray="6 7" strokeWidth="3"/>
    <circle cx="293" cy="84" r="5" fill="#67eeff"/>
    <circle cx="423" cy="79" r="5" fill="#67eeff"/>
    <path d="M178 151Q118 144 78 160" fill="none" stroke="#67eeff" strokeDasharray="6 7" strokeWidth="3"/>
    <circle cx="178" cy="151" r="5" fill="#67eeff"/>
    <circle cx="78" cy="160" r="5" fill="#67eeff"/>
    <text x="427" y="68" fill="#dffcff" fontSize="12" fontWeight="700">RADAR</text>
    <text x="25" y="158" fill="#dffcff" fontSize="12" fontWeight="700">BMS</text>
    <text x="227" y="67" fill="#dffcff" fontSize="12" fontWeight="700">GPS / GNSS</text>
  </svg>;
}

export function VehicleHeroV17() {
  return <div className="v17-hero" aria-label="Ilustración estática del vehículo inteligente AutoOS">
    <div className="v17-hero__rings" aria-hidden="true"/>
    <div className="v17-hero__vehicle"><PreviewVehicle/></div>
    <div className="v17-hero__locator v17-hero__locator--gps"><i/>GNSS / GPS</div>
    <div className="v17-hero__locator v17-hero__locator--bms"><i/>BMS / ENERGÍA</div>
    <div className="v17-hero__locator v17-hero__locator--radar"><i/>SENSORES / ADAS</div>
    <span className="v17-hero__caption">VEHÍCULO VIRTUAL · AUTOOS RTOS</span>
  </div>;
}
