import { defineConfig } from "vite"
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
    publicDir: false,
    plugins: [tailwindcss()],
    server: {
        origin: "http://localhost:5173"
    },
    build: {    
        manifest: true,
        outDir: "static/dist",
        rollupOptions: {
            input: "static/js/main.js",
            output: {
                entryFileNames: "main.js",
                assetFileNames: '[name].[ext]'
            }
        }
    }
})