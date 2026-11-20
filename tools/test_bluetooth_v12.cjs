/**
 * AUTOOS V12 — prueba aislada del controlador BLE.
 * No necesita dispositivo real; simula resultados del navegador y permisos.
 * El emparejamiento físico debe validarse manualmente en Chrome/Edge y HTTPS.
 */
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'web/public/autoos_interactive.html'),'utf8');
const start=html.indexOf('let handleBluetoothScan=async()=>{');
const end=html.indexOf('\nlet currentItem=playedList.find(',start);
if(start<0||end<0)throw new Error('No se encontró el controlador BLE V12 en el Cockpit.');
const code=html.slice(start,end)+'\nhandleBluetoothScan;';
async function testCase(label,setup,validate){
  const statuses={err:null,connected:false,connecting:false,events:[]};
  const window={isSecureContext:true,__AUTOOS_BT_CONNECTED__:false,dispatchEvent(e){statuses.events.push(e.detail);}};
  const context={window,navigator:{},document:{},btConnecting:false,
    setBtErr(value){statuses.err=value;},setBtConnected(value){statuses.connected=value;},
    setBtConnecting(value){statuses.connecting=value;},CustomEvent:class{constructor(type,{detail}){this.type=type;this.detail=detail;}},
    t(){}};
  setup(context,statuses);
  const fn=vm.runInNewContext(code,context,{timeout:1500});
  await fn();
  assert.equal(statuses.connecting,false,'La animación de espera BLE no terminó');
  validate(statuses,context);
  console.log('OK:',label);
}
(async()=>{
  await testCase('navegador sin Web Bluetooth',()=>{},s=>{
    assert.equal(s.connected,false);assert.match(s.err,/no está disponible/i);
  });
  await testCase('permiso iframe rechazado',c=>{
    c.navigator.bluetooth={requestDevice(){throw new Error('No debería escanear');}};
    c.document.permissionsPolicy={allowsFeature(){return false;}};
  },s=>{assert.match(s.err,/iframe/i);assert.equal(s.connected,false);});
  await testCase('selección cancelada',c=>{
    c.navigator.bluetooth={requestDevice:async()=>{let e=new Error('cancelado');e.name='NotFoundError';throw e;}};
  },s=>{assert.match(s.err,/canceló/i);assert.equal(s.connected,false);});
  await testCase('conexión GATT confirmada',c=>{
    c.navigator.bluetooth={requestDevice:async()=>({name:'BLE de prueba',gatt:{connect:async()=>({connected:true})},addEventListener(){}})};
  },(s,c)=>{assert.equal(s.connected,true);assert.equal(c.window.__AUTOOS_BT_CONNECTED__,true);assert.equal(s.err,null);});
  await testCase('dispositivo sin GATT',c=>{
    c.navigator.bluetooth={requestDevice:async()=>({name:'Dispositivo sin servicio GATT'})};
  },s=>{assert.equal(s.connected,false);assert.match(s.err,/GATT/);});
  console.log('RESULTADO: 5 escenarios BLE simulados aprobados.');
})().catch(e=>{console.error(e);process.exitCode=1;});
