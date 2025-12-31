import { rollup } from "rollup";

export default {
    build: {
        outDir: "frontend/static/dist",
        rollupOptions: {
            input: "frontend/static/js/main.js",
            output: {
                entryFileNames: "main.js",
                assetFileNames: '[name].[ext]'
            }
        }
    }
}