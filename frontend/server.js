import express from 'express'
import { createProxyMiddleware } from 'http-proxy-middleware'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __dirname = dirname(fileURLToPath(import.meta.url))
const app = express()

// API proxy to backend
app.use('/api', createProxyMiddleware({ target: 'http://localhost:8000', changeOrigin: true }))

// Static files
app.use(express.static(join(__dirname, 'dist')))

// SPA fallback
app.get('*', (req, res) => res.sendFile(join(__dirname, 'dist', 'index.html')))

app.listen(5173, '0.0.0.0', () => console.log('Server on http://0.0.0.0:5173'))
