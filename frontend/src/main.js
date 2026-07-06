import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import './style.css' // Optional, kannst du leeren oder löschen

const app = createApp(App)
app.use(createPinia())
app.mount('#app')