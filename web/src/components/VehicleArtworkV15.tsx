/**
 * Ilustración vectorial ORIGINAL y ESTÁTICA para AutoOS (no utiliza assets del juego).
 * Una silueta reconocible de vehículo sustituye la antigua figura abstracta.
 * SVG inline evita problemas de rutas dentro del HTML único de Streamlit.
 */
import React from 'react';

export function VehicleArtworkV15({compact=false}:{compact?:boolean}) {
  return <svg className={`v15-car-art ${compact?'v15-car-art--compact':''}`} viewBox="0 0 850 450"
    role="img" aria-label="Ilustración estática de automóvil eléctrico con sensores y ruta de navegación">
    <defs>
      <linearGradient id="v15Body" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#d7fcff"/><stop offset=".5" stopColor="#4bbce8"/><stop offset="1" stopColor="#09559e"/></linearGradient>
      <linearGradient id="v15Glass" x1="0" y1="0" x2="0" y2="1"><stop stopColor="#092c7c"/><stop offset="1" stopColor="#001a4f"/></linearGradient>
      <linearGradient id="v15Road" x1="0" x2="1"><stop stopColor="#00b1f7" stopOpacity=".02"/><stop offset=".5" stopColor="#84edff" stopOpacity=".3"/><stop offset="1" stopColor="#00b1f7" stopOpacity=".02"/></linearGradient>
    </defs>
    <g fill="none" stroke="#87f3ff" strokeOpacity=".25"><circle cx="430" cy="248" r="191"/><circle cx="430" cy="248" r="158"/><path d="M78 380L775 380M100 406L752 406M156 87L692 87"/></g>
    <path d="M40 399Q427 328 815 399L850 450H0Z" fill="url(#v15Road)"/>
    <path d="M103 353Q169 343 224 314L286 227Q315 190 376 182H550Q611 185 641 222L690 291Q753 307 767 343L780 384H106Z" fill="#031f60" stroke="#bbf6ff" strokeWidth="5"/>
    <path d="M183 318Q251 293 283 244L329 206Q355 195 391 195H549Q593 198 612 232L659 290L699 328Q597 343 434 344L188 339Z" fill="url(#v15Body)"/>
    <path d="M307 238Q326 207 386 206H436V293H266Z" fill="url(#v15Glass)" stroke="#7ae5ff" strokeWidth="3"/>
    <path d="M458 206H547Q586 211 604 240L632 286H458Z" fill="url(#v15Glass)" stroke="#7ae5ff" strokeWidth="3"/>
    <path d="M139 330Q163 322 207 325L254 336L219 352L130 349Z" fill="#00f0ff"/>
    <path d="M707 329Q745 326 770 344L764 355L686 353Z" fill="#ff4fa5"/>
    <path d="M195 343Q450 369 701 339" fill="none" stroke="#d8ffff" strokeWidth="5" opacity=".8"/>
    <path d="M280 353H610" stroke="#004ca8" strokeWidth="9" opacity=".6"/>
    <g><circle cx="270" cy="374" r="48" fill="#001431" stroke="#82f2ff" strokeWidth="7"/><circle cx="270" cy="374" r="25" fill="#0c65a8" stroke="#b1ffff" strokeWidth="4"/>
      <circle cx="654" cy="374" r="48" fill="#001431" stroke="#82f2ff" strokeWidth="7"/><circle cx="654" cy="374" r="25" fill="#0c65a8" stroke="#b1ffff" strokeWidth="4"/></g>
    <g fill="none" strokeWidth="3"><path d="M446 172V101M446 102Q340 98 322 70M446 102Q550 98 570 70" stroke="#65e9ff" strokeDasharray="8 7"/><path d="M436 175Q448 158 460 175" stroke="#fb61b0" strokeWidth="6"/></g>
    <g fill="#efffff" fontFamily="sans-serif" fontSize="16" fontWeight="800"><text x="330" y="64">GPS / GNSS</text><text x="585" y="81">RADAR</text><text x="53" y="305">BMS</text></g>
    <g fill="#55eeff"><circle cx="449" cy="102" r="7"/><circle cx="581" cy="95" r="7"/><circle cx="135" cy="309" r="7"/></g>
    <path d="M580 94L644 183M135 309L184 347" stroke="#60ecff" strokeWidth="2" strokeDasharray="5 6"/>
  </svg>;
}
