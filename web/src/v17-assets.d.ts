/** Tipado del WebP incrustado en el bundle unico de Streamlit (Vite ?inline). */
declare module '*.webp?inline' {
  const dataUri: string;
  export default dataUri;
}
