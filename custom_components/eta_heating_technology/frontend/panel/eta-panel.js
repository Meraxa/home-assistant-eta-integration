/**
 * @license
 * Copyright 2019 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */const N=globalThis,F=N.ShadowRoot&&(N.ShadyCSS===void 0||N.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,D=Symbol(),Z=new WeakMap;let de=class{constructor(e,t,s){if(this._$cssResult$=!0,s!==D)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o;const t=this.t;if(F&&e===void 0){const s=t!==void 0&&t.length===1;s&&(e=Z.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),s&&Z.set(t,e))}return e}toString(){return this.cssText}};const _e=r=>new de(typeof r=="string"?r:r+"",void 0,D),ve=(r,...e)=>{const t=r.length===1?r[0]:e.reduce((s,i,n)=>s+(a=>{if(a._$cssResult$===!0)return a.cssText;if(typeof a=="number")return a;throw Error("Value passed to 'css' function must be a 'css' function result: "+a+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+r[n+1],r[0]);return new de(t,r,D)},ye=(r,e)=>{if(F)r.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const t of e){const s=document.createElement("style"),i=N.litNonce;i!==void 0&&s.setAttribute("nonce",i),s.textContent=t.cssText,r.appendChild(s)}},G=F?r=>r:r=>r instanceof CSSStyleSheet?(e=>{let t="";for(const s of e.cssRules)t+=s.cssText;return _e(t)})(r):r;/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */const{is:xe,defineProperty:we,getOwnPropertyDescriptor:ke,getOwnPropertyNames:Ae,getOwnPropertySymbols:Se,getPrototypeOf:Ee}=Object,U=globalThis,J=U.trustedTypes,Pe=J?J.emptyScript:"",Te=U.reactiveElementPolyfillSupport,E=(r,e)=>r,B={toAttribute(r,e){switch(e){case Boolean:r=r?Pe:null;break;case Object:case Array:r=r==null?r:JSON.stringify(r)}return r},fromAttribute(r,e){let t=r;switch(e){case Boolean:t=r!==null;break;case Number:t=r===null?null:Number(r);break;case Object:case Array:try{t=JSON.parse(r)}catch{t=null}}return t}},pe=(r,e)=>!xe(r,e),Y={attribute:!0,type:String,converter:B,reflect:!1,useDefault:!1,hasChanged:pe};Symbol.metadata??=Symbol("metadata"),U.litPropertyMetadata??=new WeakMap;let y=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=Y){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){const s=Symbol(),i=this.getPropertyDescriptor(e,s,t);i!==void 0&&we(this.prototype,e,i)}}static getPropertyDescriptor(e,t,s){const{get:i,set:n}=ke(this.prototype,e)??{get(){return this[t]},set(a){this[t]=a}};return{get:i,set(a){const l=i?.call(this);n?.call(this,a),this.requestUpdate(e,l,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??Y}static _$Ei(){if(this.hasOwnProperty(E("elementProperties")))return;const e=Ee(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(E("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(E("properties"))){const t=this.properties,s=[...Ae(t),...Se(t)];for(const i of s)this.createProperty(i,t[i])}const e=this[Symbol.metadata];if(e!==null){const t=litPropertyMetadata.get(e);if(t!==void 0)for(const[s,i]of t)this.elementProperties.set(s,i)}this._$Eh=new Map;for(const[t,s]of this.elementProperties){const i=this._$Eu(t,s);i!==void 0&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){const t=[];if(Array.isArray(e)){const s=new Set(e.flat(1/0).reverse());for(const i of s)t.unshift(G(i))}else e!==void 0&&t.push(G(e));return t}static _$Eu(e,t){const s=t.attribute;return s===!1?void 0:typeof s=="string"?s:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){const e=new Map,t=this.constructor.elementProperties;for(const s of t.keys())this.hasOwnProperty(s)&&(e.set(s,this[s]),delete this[s]);e.size>0&&(this._$Ep=e)}createRenderRoot(){const e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return ye(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,s){this._$AK(e,s)}_$ET(e,t){const s=this.constructor.elementProperties.get(e),i=this.constructor._$Eu(e,s);if(i!==void 0&&s.reflect===!0){const n=(s.converter?.toAttribute!==void 0?s.converter:B).toAttribute(t,s.type);this._$Em=e,n==null?this.removeAttribute(i):this.setAttribute(i,n),this._$Em=null}}_$AK(e,t){const s=this.constructor,i=s._$Eh.get(e);if(i!==void 0&&this._$Em!==i){const n=s.getPropertyOptions(i),a=typeof n.converter=="function"?{fromAttribute:n.converter}:n.converter?.fromAttribute!==void 0?n.converter:B;this._$Em=i;const l=a.fromAttribute(t,n.type);this[i]=l??this._$Ej?.get(i)??l,this._$Em=null}}requestUpdate(e,t,s,i=!1,n){if(e!==void 0){const a=this.constructor;if(i===!1&&(n=this[e]),s??=a.getPropertyOptions(e),!((s.hasChanged??pe)(n,t)||s.useDefault&&s.reflect&&n===this._$Ej?.get(e)&&!this.hasAttribute(a._$Eu(e,s))))return;this.C(e,t,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:s,reflect:i,wrapped:n},a){s&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,a??t??this[e]),n!==!0||a!==void 0)||(this._$AL.has(e)||(this.hasUpdated||s||(t=void 0),this._$AL.set(e,t)),i===!0&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[i,n]of this._$Ep)this[i]=n;this._$Ep=void 0}const s=this.constructor.elementProperties;if(s.size>0)for(const[i,n]of s){const{wrapped:a}=n,l=this[i];a!==!0||this._$AL.has(i)||l===void 0||this.C(i,void 0,n,l)}}let e=!1;const t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(t)):this._$EM()}catch(s){throw e=!1,this._$EM(),s}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(e){}firstUpdated(e){}};y.elementStyles=[],y.shadowRootOptions={mode:"open"},y[E("elementProperties")]=new Map,y[E("finalized")]=new Map,Te?.({ReactiveElement:y}),(U.reactiveElementVersions??=[]).push("2.1.2");/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */const I=globalThis,Q=r=>r,O=I.trustedTypes,X=O?O.createPolicy("lit-html",{createHTML:r=>r}):void 0,ue="$lit$",b=`lit$${Math.random().toFixed(9).slice(2)}$`,fe="?"+b,Ce=`<${fe}>`,_=document,T=()=>_.createComment(""),C=r=>r===null||typeof r!="object"&&typeof r!="function",V=Array.isArray,Me=r=>V(r)||typeof r?.[Symbol.iterator]=="function",W=`[ 	
\f\r]`,k=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,ee=/-->/g,te=/>/g,m=RegExp(`>|${W}(?:([^\\s"'>=/]+)(${W}*=${W}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),se=/'/g,ie=/"/g,ge=/^(?:script|style|textarea|title)$/i,He=r=>(e,...t)=>({_$litType$:r,strings:e,values:t}),p=He(1),x=Symbol.for("lit-noChange"),h=Symbol.for("lit-nothing"),re=new WeakMap,$=_.createTreeWalker(_,129);function be(r,e){if(!V(r)||!r.hasOwnProperty("raw"))throw Error("invalid template strings array");return X!==void 0?X.createHTML(e):e}const ze=(r,e)=>{const t=r.length-1,s=[];let i,n=e===2?"<svg>":e===3?"<math>":"",a=k;for(let l=0;l<t;l++){const o=r[l];let c,f,d=-1,u=0;for(;u<o.length&&(a.lastIndex=u,f=a.exec(o),f!==null);)u=a.lastIndex,a===k?f[1]==="!--"?a=ee:f[1]!==void 0?a=te:f[2]!==void 0?(ge.test(f[2])&&(i=RegExp("</"+f[2],"g")),a=m):f[3]!==void 0&&(a=m):a===m?f[0]===">"?(a=i??k,d=-1):f[1]===void 0?d=-2:(d=a.lastIndex-f[2].length,c=f[1],a=f[3]===void 0?m:f[3]==='"'?ie:se):a===ie||a===se?a=m:a===ee||a===te?a=k:(a=m,i=void 0);const g=a===m&&r[l+1].startsWith("/>")?" ":"";n+=a===k?o+Ce:d>=0?(s.push(c),o.slice(0,d)+ue+o.slice(d)+b+g):o+b+(d===-2?l:g)}return[be(r,n+(r[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),s]};class M{constructor({strings:e,_$litType$:t},s){let i;this.parts=[];let n=0,a=0;const l=e.length-1,o=this.parts,[c,f]=ze(e,t);if(this.el=M.createElement(c,s),$.currentNode=this.el.content,t===2||t===3){const d=this.el.content.firstChild;d.replaceWith(...d.childNodes)}for(;(i=$.nextNode())!==null&&o.length<l;){if(i.nodeType===1){if(i.hasAttributes())for(const d of i.getAttributeNames())if(d.endsWith(ue)){const u=f[a++],g=i.getAttribute(d).split(b),v=/([.?@])?(.*)/.exec(u);o.push({type:1,index:n,name:v[2],strings:g,ctor:v[1]==="."?Ne:v[1]==="?"?Oe:v[1]==="@"?Ue:L}),i.removeAttribute(d)}else d.startsWith(b)&&(o.push({type:6,index:n}),i.removeAttribute(d));if(ge.test(i.tagName)){const d=i.textContent.split(b),u=d.length-1;if(u>0){i.textContent=O?O.emptyScript:"";for(let g=0;g<u;g++)i.append(d[g],T()),$.nextNode(),o.push({type:2,index:++n});i.append(d[u],T())}}}else if(i.nodeType===8)if(i.data===fe)o.push({type:2,index:n});else{let d=-1;for(;(d=i.data.indexOf(b,d+1))!==-1;)o.push({type:7,index:n}),d+=b.length-1}n++}}static createElement(e,t){const s=_.createElement("template");return s.innerHTML=e,s}}function w(r,e,t=r,s){if(e===x)return e;let i=s!==void 0?t._$Co?.[s]:t._$Cl;const n=C(e)?void 0:e._$litDirective$;return i?.constructor!==n&&(i?._$AO?.(!1),n===void 0?i=void 0:(i=new n(r),i._$AT(r,t,s)),s!==void 0?(t._$Co??=[])[s]=i:t._$Cl=i),i!==void 0&&(e=w(r,i._$AS(r,e.values),i,s)),e}class Re{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){const{el:{content:t},parts:s}=this._$AD,i=(e?.creationScope??_).importNode(t,!0);$.currentNode=i;let n=$.nextNode(),a=0,l=0,o=s[0];for(;o!==void 0;){if(a===o.index){let c;o.type===2?c=new H(n,n.nextSibling,this,e):o.type===1?c=new o.ctor(n,o.name,o.strings,this,e):o.type===6&&(c=new Le(n,this,e)),this._$AV.push(c),o=s[++l]}a!==o?.index&&(n=$.nextNode(),a++)}return $.currentNode=_,i}p(e){let t=0;for(const s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(e,s,t),t+=s.strings.length-2):s._$AI(e[t])),t++}}class H{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,s,i){this.type=2,this._$AH=h,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=s,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=w(this,e,t),C(e)?e===h||e==null||e===""?(this._$AH!==h&&this._$AR(),this._$AH=h):e!==this._$AH&&e!==x&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):Me(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==h&&C(this._$AH)?this._$AA.nextSibling.data=e:this.T(_.createTextNode(e)),this._$AH=e}$(e){const{values:t,_$litType$:s}=e,i=typeof s=="number"?this._$AC(e):(s.el===void 0&&(s.el=M.createElement(be(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===i)this._$AH.p(t);else{const n=new Re(i,this),a=n.u(this.options);n.p(t),this.T(a),this._$AH=n}}_$AC(e){let t=re.get(e.strings);return t===void 0&&re.set(e.strings,t=new M(e)),t}k(e){V(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let s,i=0;for(const n of e)i===t.length?t.push(s=new H(this.O(T()),this.O(T()),this,this.options)):s=t[i],s._$AI(n),i++;i<t.length&&(this._$AR(s&&s._$AB.nextSibling,i),t.length=i)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){const s=Q(e).nextSibling;Q(e).remove(),e=s}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}}class L{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,s,i,n){this.type=1,this._$AH=h,this._$AN=void 0,this.element=e,this.name=t,this._$AM=i,this.options=n,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=h}_$AI(e,t=this,s,i){const n=this.strings;let a=!1;if(n===void 0)e=w(this,e,t,0),a=!C(e)||e!==this._$AH&&e!==x,a&&(this._$AH=e);else{const l=e;let o,c;for(e=n[0],o=0;o<n.length-1;o++)c=w(this,l[s+o],t,o),c===x&&(c=this._$AH[o]),a||=!C(c)||c!==this._$AH[o],c===h?e=h:e!==h&&(e+=(c??"")+n[o+1]),this._$AH[o]=c}a&&!i&&this.j(e)}j(e){e===h?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}}class Ne extends L{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===h?void 0:e}}class Oe extends L{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==h)}}class Ue extends L{constructor(e,t,s,i,n){super(e,t,s,i,n),this.type=5}_$AI(e,t=this){if((e=w(this,e,t,0)??h)===x)return;const s=this._$AH,i=e===h&&s!==h||e.capture!==s.capture||e.once!==s.once||e.passive!==s.passive,n=e!==h&&(s===h||i);i&&this.element.removeEventListener(this.name,this,s),n&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}}class Le{constructor(e,t,s){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(e){w(this,e)}}const We=I.litHtmlPolyfillSupport;We?.(M,H),(I.litHtmlVersions??=[]).push("3.3.3");const Be=(r,e,t)=>{const s=t?.renderBefore??e;let i=s._$litPart$;if(i===void 0){const n=t?.renderBefore??null;s._$litPart$=i=new H(e.insertBefore(T(),n),n,void 0,t??{})}return i._$AI(r),i};/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */const q=globalThis;class P extends y{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=Be(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return x}}P._$litElement$=!0,P.finalized=!0,q.litElementHydrateSupport?.({LitElement:P});const Ke=q.litElementPolyfillSupport;Ke?.({LitElement:P});(q.litElementVersions??=[]).push("4.2.2");const S=[{id:"live",label:"Live"},{id:"kessel",label:"Kessel"},{id:"puffer",label:"Puffer"},{id:"heizkreis",label:"Heizkreis"},{id:"wasser",label:"Warmwasser"},{id:"lager",label:"Lager"},{id:"anlage",label:"Anlage"}],Fe={Kessel:"kessel",PufferFlex:"puffer",Heizkreis:"heizkreis",Wasser:"wasser",Lager:"lager",Sys:"anlage"},De=new Set(["PufferFlex.Puffer","Heizkreis.Heizkreis","Wasser.Warmwasser","Wasser.Zirkulation"]),Ie=new Set(["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"]),Ve=new Set(["Kalibrierwert","Sensor Typ","Fixwert","Extrapol","Impulse pro Liter","Zustand"]),qe=[{key:"state",path:"Kessel.Kessel"},{key:"fault",path:"Sys.Störmeldung"},{key:"boilerFault",path:"Kessel.Kessel.Kesselstörmeldung"},{key:"errors",path:"active_errors"},{key:"outdoor",path:"Sys.Außentemperatur.Außentemperaturfühler"},{key:"flow",path:"Kessel.Eingänge.Wärmemessung.Vorlauf"},{key:"returnTemp",path:"Kessel.Ausgänge.Rücklaufmischer.Ist Temperatur"},{key:"bufferTop",path:"PufferFlex.Puffer.Erzeuger Kessel/Puffer.Puffer oben",fallback:".Puffer oben"},{key:"bufferBottom",path:"PufferFlex.Puffer.Erzeuger Kessel/Puffer.Puffer unten",fallback:".Puffer unten"},{key:"dhw",path:"Wasser.Eingänge.Warmwasser"},{key:"dhwSet",path:"Wasser.Warmwasser.Soll Temperatur"},{key:"hopper",path:"Kessel.Kessel.Pelletsbehälter.Inhalt Pelletsbehälter"},{key:"stock",path:"Lager.Vorrat"},{key:"stockMax",path:"Lager.Vorrat.Maximaler Vorrat"},{key:"energy",path:"Kessel.Zählerstände.Wärmemessung.Energie"},{key:"fan",path:"Kessel.Ausgänge.Abgasgebläse"},{key:"ignition",path:"Kessel.Ausgänge.Zündung"},{key:"power",path:"Kessel.Kessel.Vorlauf.Angeforderte Leistung"},{key:"hkFlow",path:"Heizkreis.Heizkreis.Vorlauf",fallback:".Vorlauf"},{key:"hkReturn",path:"Heizkreis.Heizkreis.Rücklauf"},{key:"hkSet",path:"Heizkreis.Ausgänge.Heizkreismischer.Soll Temperatur"},{key:"primaryFlow",path:"Wasser.Eingänge.Primär Vorlauf"},{key:"flowRate",path:"Wasser.Warmwasser.Sekundär Durchfluss"},{key:"bufferPump",path:"Wasser.Ausgänge.Pufferpumpe.Ausgang"},{key:"mixPump",path:"Wasser.Ausgänge.Beimischpumpe.Ausgang"}],je=["Kessel.Sonstiges.Ein/Aus Taste","Heizkreis.Sonstiges.Heizen Taste","Heizkreis.Sonstiges.Auto Taste","Heizkreis.Sonstiges.Absenken Taste","Heizkreis.Sonstiges.Kommen Taste","Heizkreis.Sonstiges.Gehen Taste","Heizkreis.Sonstiges.Ein/Aus Taste","PufferFlex.Puffer.Erzeuger Kessel/Puffer.Starten nach zusätzlichen Kriterien.Extra laden.Sofort laden","PufferFlex.Puffer.Warmwasserbereich.Warmwasser sofort laden","Wasser.Sonstiges.Ein/Aus Taste"],Ze=new Set(["Kessel.Sonstiges.Ein/Aus Taste","Heizkreis.Sonstiges.Ein/Aus Taste","Wasser.Sonstiges.Ein/Aus Taste","Heizkreis.Heizkreis.Estrich.Start Estrich ausheizen"]),ne=new Set(["Eingänge","Ausgänge","Kessel","Vorrat","Außentemperatur","Störmeldung","Vorlauf","Rücklauf"]),Ge=new Set(["Heizversuch","Zünden","Heizen","Glutabbrand","Glutabbrand wegen Entaschung","Füllen","Entaschen","Stoker leeren"]),Je=r=>!!r&&Ge.has(r);function z(r){return r.startsWith("/")?["Weitere",r]:r.split(".").filter(e=>e.length>0)}function Ye(r){return Fe[z(r)[0]??""]??"anlage"}function Qe(r){const e=z(r);if(e[0]==="Weitere"||e[0]==="active_errors")return e[0]==="active_errors"?"Störung":"Weitere";const t=e.slice(0,2).join(".");return De.has(t)&&e[2]?e[2]:e[1]??e[0]??"Allgemein"}function A(r){const e=z(r);return e[e.length-1]??r}function Xe(r){return z(r).some(e=>Ie.has(e)||e.startsWith("Zeitfenster")||e.startsWith("Wert außerhalb"))}function et(r){const e=z(r),t=e[e.length-1]??"";return Ve.has(t)?!0:e.some(s=>/^Lin [xy]\d*$/.test(s)||/^Lag [xy]$/.test(s))}function tt(r){const e=new Set;for(const t of r){if(t.startsWith("/"))continue;const s=`${t}.`;r.some(i=>i.startsWith(s))&&e.add(t)}return e}const R=(r,e)=>r.path.localeCompare(e.path,"de");function ae(r,e){const t=tt(r.map(i=>i.path)),s=new Map;for(const i of r){if(i.disabled||Ye(i.path)!==e||t.has(i.path))continue;const n=Qe(i.path),a=`${e}/${n}`;let l=s.get(a);l||(l={id:a,title:n,switches:[],tiles:[],details:[],schedule:[]},s.set(a,l)),i.domain==="switch"?l.switches.push(i):Xe(i.path)?l.schedule.push(i):et(i.path)?l.details.push(i):l.tiles.push(i)}for(const i of s.values())i.switches.sort(R),i.tiles.sort(R),i.details.sort(R),i.schedule.sort(R);return[...s.values()].sort((i,n)=>i.title.localeCompare(n.title,"de"))}function me(r){const e=new Map;for(const t of r)!t.disabled&&!e.has(t.path)&&e.set(t.path,t);return e}function st(r,e){const t=qe.find(n=>n.key===e);if(!t)return;const i=me(r).get(t.path);if(i)return i;if(t.fallback)return r.find(n=>!n.disabled&&!n.path.startsWith("/")&&n.path.endsWith(t.fallback??""))}function it(r,e){const t=me(r);return e.flatMap(s=>{const i=t.get(s);return i?[i]:[]})}function oe(r){return S.some(e=>e.id===r)}function rt(r){const e=[];for(const t of r??[]){const s=t.lc??t.lu,i=s!==void 0?s*1e3:Date.parse(t.last_changed??t.last_updated??""),n=Number.parseFloat(t.s??t.state??"");Number.isFinite(i)&&Number.isFinite(n)&&e.push({t:i,v:n})}return e}function nt(r,e){const t=new Map;for(const s of r){const i=Math.floor(s.t/e)*e,n=t.get(i)??{sum:0,n:0};n.sum+=s.v,n.n+=1,t.set(i,n)}return[...t.entries()].sort(([s],[i])=>s-i).map(([s,i])=>({t:s,v:i.sum/i.n}))}const at=ve`
  :host {
    --bg: #100c09;
    --text: #f6efe6;
    --muted: #b5a89a;
    --faint: #7d7268;
    --stroke: rgba(255, 236, 214, 0.1);
    --stroke-strong: rgba(255, 236, 214, 0.18);
    --card: linear-gradient(180deg, rgba(255, 244, 230, 0.07), rgba(255, 244, 230, 0.03));
    --rail: rgba(16, 12, 9, 0.88);
    --accent: #f59e0b;
    --ember: #fb7185;
    --water: #67e8f9;
    --buffer: #c4b5fd;
    --ok: #34d399;
    --field: rgba(0, 0, 0, 0.28);
    --shadow: 0 18px 40px rgba(0, 0, 0, 0.28);
    color-scheme: dark;
    display: block;
    height: 100vh;
    height: 100dvh;
    overflow: hidden;
    color: var(--text);
    font-family: Inter, system-ui, sans-serif;
    background:
      radial-gradient(900px 420px at 0% -10%, rgba(245, 158, 11, 0.18), transparent 60%),
      radial-gradient(700px 420px at 100% 0%, rgba(251, 113, 133, 0.12), transparent 55%),
      var(--bg);
  }
  :host([theme="classic"]) {
    color-scheme: light;
    --bg: #f4efe8;
    --text: #2a2118;
    --muted: #6d5e51;
    --faint: #97887a;
    --stroke: rgba(42, 33, 24, 0.1);
    --stroke-strong: rgba(42, 33, 24, 0.16);
    --card: linear-gradient(180deg, #fffdf9, #f7f1e8);
    --rail: rgba(255, 252, 247, 0.94);
    --field: #fff;
    --shadow: 0 14px 30px rgba(42, 33, 24, 0.08);
    background:
      radial-gradient(900px 420px at 0% -10%, rgba(245, 158, 11, 0.2), transparent 60%),
      var(--bg);
  }
  * { box-sizing: border-box; }
  button, input { font: inherit; color: inherit; }
  button { cursor: pointer; }
  .shell { display: flex; height: 100%; }
  .rail {
    width: 220px;
    flex: none;
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 22px 14px;
    border-right: 1px solid var(--stroke);
    background: var(--rail);
    backdrop-filter: blur(16px);
  }
  .brand { padding: 4px 10px 16px; }
  .brand b { display: block; font-size: 18px; letter-spacing: -0.03em; }
  .brand span { color: var(--muted); font-size: 12px; }
  .nav-btn, .room-head, .tile, .switch, .text-btn {
    border: 1px solid transparent;
    background: transparent;
    text-align: left;
  }
  .nav-btn {
    display: flex;
    align-items: center;
    gap: 10px;
    border-radius: 12px;
    padding: 10px 12px;
    color: var(--muted);
  }
  .nav-btn[aria-current="page"] { background: rgba(245, 158, 11, 0.14); color: var(--text); }
  .nav-btn svg { width: 18px; height: 18px; flex: none; }
  .main { flex: 1; overflow: auto; padding: 28px 32px 48px; }
  h1 { margin: 0 0 4px; font-size: 28px; letter-spacing: -0.04em; }
  h2 { margin: 18px 0 8px; font-size: 15px; font-weight: 650; }
  .sub { margin: 0 0 18px; color: var(--muted); }
  .banner {
    margin-bottom: 16px;
    padding: 12px 14px;
    border-radius: 14px;
    border: 1px solid rgba(251, 113, 133, 0.4);
    background: rgba(251, 113, 133, 0.12);
  }
  .banner.warn { border-color: rgba(245, 158, 11, 0.45); background: rgba(245, 158, 11, 0.12); }
  .hero, .card {
    border: 1px solid var(--stroke);
    border-radius: 20px;
    background: var(--card);
    box-shadow: var(--shadow);
  }
  .hero { padding: 22px; margin-bottom: 16px; }
  .hero-top { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; }
  .state { font-size: 34px; letter-spacing: -0.04em; margin: 0; }
  .state.burn { color: var(--accent); }
  .state.fault { color: var(--ember); }
  .meta { color: var(--muted); font-size: 13px; }
  .kpis, .tiles { display: grid; grid-template-columns: repeat(auto-fill, minmax(168px, 1fr)); gap: 10px; }
  .tile {
    border-color: var(--stroke);
    border-radius: 16px;
    padding: 12px 14px;
    background: rgba(255, 255, 255, 0.03);
  }
  :host([theme="classic"]) .tile { background: rgba(255, 255, 255, 0.7); }
  .tile b { display: block; font-size: 22px; letter-spacing: -0.03em; font-weight: 620; }
  .tile span, .switch span.name { display: block; color: var(--muted); font-size: 12px; }
  .bar { height: 6px; border-radius: 99px; background: rgba(255, 255, 255, 0.08); margin-top: 8px; overflow: hidden; }
  .bar i { display: block; height: 100%; background: var(--accent); }
  .schematic { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; margin: 16px 0; }
  .node { padding: 14px; border-radius: 16px; border: 1px solid var(--stroke); min-height: 112px; }
  .node.kessel { background: rgba(245, 158, 11, 0.1); }
  .node.puffer { background: rgba(196, 181, 253, 0.1); }
  .node.kreis { background: rgba(251, 113, 133, 0.08); }
  .node.wasser { background: rgba(103, 232, 249, 0.08); }
  .node strong { display: block; margin-bottom: 8px; }
  .node p { margin: 2px 0; font-size: 13px; color: var(--muted); }
  .node p b { color: var(--text); font-weight: 600; }
  .node.burn { box-shadow: inset 0 0 0 1px rgba(245, 158, 11, 0.7); }
  .controls { display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0 18px; }
  .switch, .text-btn {
    border-color: var(--stroke-strong);
    border-radius: 999px;
    padding: 8px 12px;
    background: var(--field);
  }
  .switch[aria-pressed="true"] { border-color: rgba(245, 158, 11, 0.8); background: rgba(245, 158, 11, 0.16); }
  .room { margin-bottom: 12px; }
  .room-head {
    width: 100%;
    display: flex;
    justify-content: space-between;
    padding: 12px 4px;
    border-bottom: 1px solid var(--stroke);
  }
  .room-head span { color: var(--faint); }
  .search {
    width: min(420px, 100%);
    margin-bottom: 14px;
    border-radius: 12px;
    border: 1px solid var(--stroke-strong);
    background: var(--field);
    padding: 10px 12px;
  }
  .details { margin-top: 8px; }
  .details summary { color: var(--muted); cursor: pointer; }
  .sheet, .dialog {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.45);
    display: flex;
    align-items: flex-end;
    justify-content: center;
    z-index: 20;
  }
  .sheet article, .dialog article {
    width: min(760px, 100%);
    background: var(--rail);
    border-radius: 20px 20px 0 0;
    padding: 18px 18px 28px;
    border: 1px solid var(--stroke);
  }
  .dialog { align-items: center; }
  .dialog article { width: min(420px, calc(100% - 32px)); border-radius: 20px; }
  svg.chart { width: 100%; height: 220px; }
  .bottom { display: none; }
  @media (max-width: 960px) {
    .rail { display: none; }
    .main { padding: 18px 16px 96px; }
    .schematic { grid-template-columns: 1fr 1fr; }
    .bottom {
      display: flex;
      position: fixed;
      left: 0; right: 0; bottom: 0;
      gap: 2px;
      padding: 6px 6px calc(8px + env(safe-area-inset-bottom));
      background: var(--rail);
      border-top: 1px solid var(--stroke);
      z-index: 10;
    }
    .bottom button {
      flex: 1;
      border: 0;
      background: transparent;
      color: var(--faint);
      font-size: 10px;
      padding: 6px 0;
    }
    .bottom button[aria-current="page"] { color: var(--accent); }
  }
`,$e="eta-heating.groups.v1",ot=1440*60*1e3,lt=300*1e3,ht=new Set(["","xxx","unknown","unavailable","none","None"]),le=new Set(["","0","Aus","Keine","Nein","xxx","unknown","unavailable","none","None"]),he={de:{title:"ETA",tag:"Heizung",liveSub:"Zustand der Anlage, ohne automatische Regelung.",roomSub:"Messpunkte und Handschalter aus diesem Anlagenteil.",empty:"Keine ETA-Entitäten geladen. In den Integrationsoptionen Messpunkte auswählen, danach Home Assistant neu starten.",offline:"Die ETA ist nicht erreichbar. Angezeigte Werte können veraltet sein.",unavailable:r=>`${r} Messpunkte sind nicht verfügbar.`,disabled:r=>`${r} Messpunkte sind deaktiviert.`,fault:"Störmeldung",errors:r=>`${r} aktive Fehler`,host:"Anlage",controls:"Handsteuerung",confirmTitle:"Schalter betätigen?",confirmBody:"Das schreibt den Zustand direkt an die ETA. Eine Regelung übernimmt das nicht wieder.",cancel:"Abbrechen",apply:"Übernehmen",history:"Letzte 24 Stunden",noHistory:"Für diesen Messpunkt liegen keine Zahlen im Recorder.",close:"Schließen",search:"Messpunkt suchen",details:"Kalibrierung und Sensorzustand",schedule:"Zeitprogramm",more:"weitere",stock:"Vorrat",outdoor:"Außen",flow:"Kessel Vorlauf",returnTemp:"Kessel Rücklauf",bufferTop:"Puffer oben",bufferBottom:"Puffer unten",dhw:"Warmwasser",hopper:"Pelletsbehälter",hkFlow:"Heizkreis Vorlauf",hkReturn:"Heizkreis Rücklauf",power:"Anforderung",fan:"Abgasgebläse",ignition:"Zündung",flowRate:"Durchfluss",energy:"Wärme gesamt",kessel:"Kessel",puffer:"Puffer",heizkreis:"Heizkreis",wasser:"Warmwasser"},en:{title:"ETA",tag:"Heating",liveSub:"Plant status. Nothing here runs a control loop.",roomSub:"Readings and manual switches for this part of the plant.",empty:"No ETA entities loaded. Choose data points in the integration options, then restart Home Assistant.",offline:"The ETA is unreachable. Shown values may be stale.",unavailable:r=>`${r} data points are unavailable.`,disabled:r=>`${r} data points are disabled.`,fault:"Fault",errors:r=>`${r} active errors`,host:"Plant",controls:"Manual control",confirmTitle:"Send this switch?",confirmBody:"This writes the state straight to the ETA. No controller sets it back.",cancel:"Cancel",apply:"Apply",history:"Last 24 hours",noHistory:"The recorder has no numeric history for this point.",close:"Close",search:"Find a data point",details:"Calibration and sensor health",schedule:"Schedule",more:"more",stock:"Store",outdoor:"Outside",flow:"Boiler flow",returnTemp:"Boiler return",bufferTop:"Buffer top",bufferBottom:"Buffer bottom",dhw:"Hot water",hopper:"Pellet hopper",hkFlow:"Circuit flow",hkReturn:"Circuit return",power:"Demand",fan:"Flue fan",ignition:"Ignition",flowRate:"Flow",energy:"Heat total",kessel:"Boiler",puffer:"Buffer",heizkreis:"Circuit",wasser:"Hot water"}},ct=r=>r?.toLowerCase().startsWith("en")?he.en:he.de,ce=(r,e,t)=>{if(r===void 0||ht.has(r))return"–";if(/^-?\d+(\.\d+)?$/.test(r)){const s=Number(r),i=Number.isInteger(s)?0:1,n=s.toLocaleString(t,{maximumFractionDigits:i});return e?`${n} ${e}`:n}return r},dt=r=>p`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d=${r} /></svg>`,pt={live:"M12 3v3M12 18v3M3 12h3M18 12h3M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z",kessel:"M4 20V10h16v10M8 10V6h8v4M9 14h.01M12 14h.01M15 14h.01",puffer:"M7 3h10v18H7zM7 8h10M7 16h10",heizkreis:"M4 12h16M7 12a5 5 0 0 1 10 0",wasser:"M12 3s6 6.2 6 10a6 6 0 0 1-12 0c0-3.8 6-10 6-10z",lager:"M3 9 12 4l9 5-9 5-9-5zM3 14l9 5 9-5",anlage:"M12 3 4 7v6c0 5 3.4 7.6 8 8 4.6-.4 8-3 8-8V7l-8-4z"},ut=()=>{const r=localStorage.getItem($e);if(r!==null)try{const e=JSON.parse(r);return new Set(Array.isArray(e)?e.filter(t=>typeof t=="string"):[])}catch{return new Set}},j=class j extends P{constructor(){super(...arguments),this._screen=oe(location.hash.slice(1))?location.hash.slice(1):"live",this._query="",this._collapsed=ut(),this._ids=new Set,this._resolving=!1,this._chartToken=0,this._onHash=()=>{const e=location.hash.slice(1);oe(e)&&e!==this._screen&&(this._screen=e,this._query="",this.requestUpdate())},this._onKey=e=>{e.key==="Escape"&&(this._pending=void 0,this._chart=void 0,this.requestUpdate())}}set hass(e){const t=this._hass;this._hass=e,this._applyTheme(e),this._payload||this._resolve(),(!t||t.language!==e.language||[...this._ids].some(i=>t.states[i]?.state!==e.states[i]?.state))&&this.requestUpdate()}get hass(){return this._hass}connectedCallback(){super.connectedCallback(),window.addEventListener("hashchange",this._onHash),window.addEventListener("keydown",this._onKey)}disconnectedCallback(){window.removeEventListener("hashchange",this._onHash),window.removeEventListener("keydown",this._onKey),super.disconnectedCallback()}_applyTheme(e){const t=e.themes?.darkMode,s=typeof t=="boolean"?t?"dark":"classic":"dark";this.getAttribute("theme")!==s&&this.setAttribute("theme",s)}async _resolve(){if(!(!this._hass||this._resolving)){this._resolving=!0;try{this._payload=await this._hass.callWS({type:"eta_heating_technology/panel_entities"}),this._ids=new Set(this._payload.entries.flatMap(e=>e.entities.map(t=>t.entity_id))),this._error=void 0}catch(e){this._error=e instanceof Error?e.message:String(e)}finally{this._resolving=!1,this.requestUpdate()}}}_lang(){return this._hass?.language??"de"}_state(e){if(!(!e||!this._hass))return this._hass.states[e.entity_id]}_value(e){const t=this._state(e),s=t?.attributes.unit_of_measurement;return ce(t?.state,typeof s=="string"?s:void 0,this._lang())}_go(e){location.hash=e}_entities(){return this._payload?.entries[0]?.entities??[]}_toggleRoom(e){const t=this._entities();if(!this._collapsed){this._collapsed=new Set;for(const s of S)if(s.id!=="live")for(const i of ae(t,s.id))ne.has(i.title)||this._collapsed.add(i.id)}this._collapsed.has(e.id)?this._collapsed.delete(e.id):this._collapsed.add(e.id),localStorage.setItem($e,JSON.stringify([...this._collapsed])),this.requestUpdate()}_open(e){return this._collapsed?!this._collapsed.has(e.id):ne.has(e.title)}async _setSwitch(e,t){this._pending=void 0,await this._hass?.callService("switch",t?"turn_on":"turn_off",{entity_id:e.entity_id}),this.requestUpdate()}_ask(e){const t=this._state(e)?.state!=="on";if(Ze.has(e.path)){this._pending={entity:e,turnOn:t},this.requestUpdate();return}this._setSwitch(e,t)}async _openChart(e){const t=this._state(e)?.state;if(e.domain!=="sensor"||t===void 0||!/^-?\d+(\.\d+)?$/.test(t))return;const s=++this._chartToken;this._chart={entity:e,loading:!0},this.requestUpdate();try{const i=await this._hass?.callWS({type:"history/history_during_period",start_time:new Date(Date.now()-ot).toISOString(),end_time:new Date().toISOString(),entity_ids:[e.entity_id],minimal_response:!0,no_attributes:!0,significant_changes_only:!0});if(s!==this._chartToken)return;this._chart={entity:e,points:nt(rt(i?.[e.entity_id]),lt)}}catch{if(s!==this._chartToken)return;this._chart={entity:e,failed:!0}}this.requestUpdate()}_switchRow(e,t){return e.length?p`
      <h2>${t}</h2>
      <div class="controls">
        ${e.map(s=>p`
            <button class="switch" aria-pressed=${this._state(s)?.state==="on"} @click=${()=>this._ask(s)}>
              <span class="name">${A(s.path)}</span>
            </button>
          `)}
      </div>
    `:h}_tile(e){return p`
      <button class="tile" @click=${()=>this._openChart(e)}>
        <span>${A(e.path)}</span>
        <b>${this._value(e)}</b>
      </button>
    `}_ratio(e,t){const s=Number(this._state(e)?.state),i=Number(this._state(t)?.state);if(!Number.isFinite(s)||!Number.isFinite(i)||i<=0)return h;const n=Math.max(0,Math.min(100,s/i*100));return p`<div class="bar"><i style=${`width:${n}%`}></i></div>`}_live(e){const t=this._entities(),s=g=>st(t,g),i=s("state"),n=this._state(i)?.state,a=Je(n),l=this._state(s("fault"))?.state,o=this._state(s("errors"))?.state,c=!!l&&!le.has(l),f=!!o&&!le.has(o),d=this._payload?.entries[0],u=(g,v)=>g?p`<p>${v} <b>${this._value(g)}</b></p>`:h;return p`
      ${c?p`<div class="banner">${e.fault}: ${l}</div>`:h}
      ${f?p`<div class="banner">${e.errors(o??"")}</div>`:h}
      <section class="hero">
        <div class="hero-top">
          <div>
            <p class="state ${a?"burn":""} ${n==="Störung"?"fault":""}">${ce(n,void 0,this._lang())}</p>
            <p class="meta">${e.host} ${d?.host??"–"}${d?.port?`:${d.port}`:""}</p>
          </div>
          <div class="meta">
            ${u(s("power"),e.power)}
            ${u(s("fan"),e.fan)}
            ${u(s("ignition"),e.ignition)}
          </div>
        </div>
      </section>
      <div class="schematic">
        <div class="node kessel ${a?"burn":""}">
          <strong>${e.kessel}</strong>
          ${u(s("flow"),e.flow)}
          ${u(s("returnTemp"),e.returnTemp)}
          ${u(s("hopper"),e.hopper)}
        </div>
        <div class="node puffer">
          <strong>${e.puffer}</strong>
          ${u(s("bufferTop"),e.bufferTop)}
          ${u(s("bufferBottom"),e.bufferBottom)}
        </div>
        <div class="node kreis">
          <strong>${e.heizkreis}</strong>
          ${u(s("hkFlow"),e.hkFlow)}
          ${u(s("hkReturn"),e.hkReturn)}
        </div>
        <div class="node wasser">
          <strong>${e.wasser}</strong>
          ${u(s("dhw"),e.dhw)}
          ${u(s("flowRate"),e.flowRate)}
        </div>
      </div>
      <div class="kpis">
        ${this._kpi(s("outdoor"),e.outdoor)}
        ${this._kpi(s("stock"),e.stock,s("stockMax"))}
        ${this._kpi(s("energy"),e.energy)}
        ${this._kpi(s("dhwSet"),"Soll")}
        ${this._kpi(s("bufferPump"),"Pufferpumpe")}
        ${this._kpi(s("mixPump"),"Beimischpumpe")}
      </div>
      ${this._switchRow(it(t,je),e.controls)}
    `}_kpi(e,t,s){return e?p`
      <button class="tile" @click=${()=>this._openChart(e)}>
        <span>${t}</span>
        <b>${this._value(e)}</b>
        ${this._ratio(e,s)}
      </button>
    `:h}_rooms(e){const t=this._query.trim().toLowerCase(),s=ae(this._entities(),this._screen).map(i=>({...i,switches:i.switches.filter(n=>!t||n.path.toLowerCase().includes(t)),tiles:i.tiles.filter(n=>!t||n.path.toLowerCase().includes(t)),details:i.details.filter(n=>!t||n.path.toLowerCase().includes(t)),schedule:i.schedule.filter(n=>!t||n.path.toLowerCase().includes(t))})).filter(i=>i.switches.length+i.tiles.length+i.details.length+i.schedule.length>0);return p`
      <input class="search" type="search" placeholder=${e.search} .value=${this._query} @input=${i=>{this._query=i.target.value,this.requestUpdate()}} />
      ${s.map(i=>{const n=i.tiles.length+i.switches.length,a=t.length>0||this._open(i);return p`
          <section class="room">
            <button class="room-head" aria-expanded=${a} @click=${()=>this._toggleRoom(i)}>
              <b>${i.title}</b><span>${n}</span>
            </button>
            ${a?p`
                  <div class="controls">
                    ${i.switches.map(l=>p`
                        <button class="switch" aria-pressed=${this._state(l)?.state==="on"} @click=${()=>this._ask(l)}>
                          <span class="name">${A(l.path)}</span>
                        </button>
                      `)}
                  </div>
                  <div class="tiles">${i.tiles.map(l=>this._tile(l))}</div>
                  ${i.schedule.length?p`<details class="details"><summary>${e.schedule} (${i.schedule.length})</summary><div class="tiles">${i.schedule.map(l=>this._tile(l))}</div></details>`:h}
                  ${i.details.length?p`<details class="details"><summary>${e.details} (${i.details.length})</summary><div class="tiles">${i.details.map(l=>this._tile(l))}</div></details>`:h}
                `:h}
          </section>
        `})}
    `}_chartSvg(e){const t=Math.min(...e.map(o=>o.v)),i=Math.max(...e.map(o=>o.v))-t||1,n=720,a=200,l=e.map((o,c)=>{const f=c/Math.max(e.length-1,1)*n,d=a-(o.v-t)/i*(a-20)-10;return`${c===0?"M":"L"}${f.toFixed(1)},${d.toFixed(1)}`}).join(" ");return p`<svg class="chart" viewBox="0 0 ${n} ${a}" role="img"><path d=${l} fill="none" stroke="#f59e0b" stroke-width="3" /></svg>`}render(){const e=ct(this._hass?.language),t=this._entities(),s=S.find(o=>o.id===this._screen)??S[0],i=t.filter(o=>this._state(o)?.state==="unavailable"&&!o.disabled),n=t.length>0&&i.length===t.filter(o=>!o.disabled).length,a=t.filter(o=>o.disabled).length,l=o=>S.map(c=>p`
          <button class=${o} aria-current=${c.id===this._screen?"page":h} @click=${()=>this._go(c.id)}>
            ${o==="nav-btn"?dt(pt[c.id]):h}
            ${c.id==="live",c.label}
          </button>
        `);return p`
      <div class="shell">
        <nav class="rail" aria-label="ETA">
          <div class="brand"><b>${e.title}</b><span>${e.tag}</span></div>
          ${l("nav-btn")}
        </nav>
        <main class="main">
          <h1>${s?.label}</h1>
          <p class="sub">${this._screen==="live"?e.liveSub:e.roomSub}</p>
          ${this._error?p`<div class="banner">${this._error}</div>`:h}
          ${n?p`<div class="banner">${e.offline}</div>`:h}
          ${!n&&i.length?p`<div class="banner warn">${e.unavailable(i.length)}</div>`:h}
          ${a?p`<div class="banner warn">${e.disabled(a)}</div>`:h}
          ${t.length===0&&this._payload?p`<div class="banner warn">${e.empty}</div>`:h}
          ${this._screen==="live"?this._live(e):this._rooms(e)}
        </main>
        <nav class="bottom">${l("")}</nav>
      </div>
      ${this._chart?p`
            <div class="sheet" @click=${o=>{o.target===o.currentTarget&&(this._chart=void 0,this.requestUpdate())}}>
              <article>
                <h2>${A(this._chart.entity.path)}</h2>
                <p class="sub">${e.history} · ${this._value(this._chart.entity)}</p>
                ${this._chart.loading?p`<p class="sub">…</p>`:this._chart.points&&this._chart.points.length>1?this._chartSvg(this._chart.points):p`<p>${e.noHistory}</p>`}
                <button class="text-btn" @click=${()=>{this._chart=void 0,this.requestUpdate()}}>${e.close}</button>
              </article>
            </div>
          `:h}
      ${this._pending?p`
            <div class="dialog">
              <article>
                <h2>${e.confirmTitle}</h2>
                <p>${A(this._pending.entity.path)}. ${e.confirmBody}</p>
                <div class="controls">
                  <button class="text-btn" @click=${()=>{this._pending=void 0,this.requestUpdate()}}>${e.cancel}</button>
                  <button class="switch" aria-pressed="true" @click=${()=>this._pending&&this._setSwitch(this._pending.entity,this._pending.turnOn)}>${e.apply}</button>
                </div>
              </article>
            </div>
          `:h}
    `}};j.styles=at;let K=j;customElements.define("eta-heating-panel",K);
