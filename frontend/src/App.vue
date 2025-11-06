<script setup>
import { ref, nextTick } from 'vue'
import Keyboard from 'simple-keyboard'
import 'simple-keyboard/build/css/index.css'
import Hangul from 'hangul-js'

const text = ref('')
const result = ref(null)
const loading = ref(false)
const error = ref(null)
const showResult = ref(false)
const showKeyboard = ref(false)

let keyboard = null

// Séparation committed / buffer
let committed = ''         // texte validé (sans la composition en cours)
let buffer = []            // liste de jamos en cours (ex: ['ㅇ','ㅏ','ㄴ'])

async function initKeyboard() {
  await nextTick()

  keyboard = new Keyboard({
    layout: {
      default: [
        "ㅂ ㅃ ㅈ ㅉ ㄷ ㄸ ㄱ ㄲ ㅅ ㅆ ㅛ ㅕ ㅑ ㅒ ㅖ",
        "ㅁ ㄴ ㅇ ㄹ ㅎ ㅗ ㅓ ㅏ ㅣ",
        "ㅋ ㅌ ㅊ ㅍ ㅠ ㅜ ㅡ",
        "{space} {bksp}"
      ]
    },
    display: {
      "{space}": "⎵",
      "{bksp}": "⌫"
    },
    onKeyPress: handleKey
  })
}

function handleKey(button) {
  if (button === "{space}") {
    commitBuffer()
    committed += ' '
    updateText() // show committed + space
    return
  }

  if (button === "{bksp}") {
    // si on a des jamos en composition -> on retire la dernière jamo du buffer
    if (buffer.length > 0) {
      buffer.pop()
      updateText()
      return
    }
    // sinon, on supprime le dernier caractère du texte "committed"
    if (committed.length > 0) {
      // supprimer correctement le dernier *grapheme cluster* (pour coréen)
      committed = removeLastGrapheme(committed)
      updateText()
    }
    return
  }

  // touche jamo normale : on ajoute au buffer et on met à jour l'aperçu
  buffer.push(button)
  updateText()
}

// met à jour text.value en combinant committed + composition (assemble(buffer))
function updateText() {
  const composed = buffer.length ? Hangul.assemble(buffer) : ''
  text.value = committed + composed
}

// lorsque l'utilisateur confirme la composition (ex: espace) ou veut "verrouiller" la composition
function commitBuffer() {
  if (buffer.length > 0) {
    const composed = Hangul.assemble(buffer)
    committed += composed
    buffer = []
  }
}


// helper pour supprimer le dernier grapheme (caractère coréen complet) de committed
function removeLastGrapheme(s) {
  // approche simple : on utilise Hangul.disassemble pour retirer le dernier syllabe proprement
  if (!s) return ''
  // si le dernier index est un espace, juste pop
  if (s.slice(-1) === ' ') return s.slice(0, -1)

  // on essaye d'identifier la dernière syllabe
  // découper en tableau de syllabes (approximation via split(""))
  // plus robuste : utiliser Hangul.disassemble/assemble
  // méthode : retirer le dernier codepoint (Unicode) — suffit généralement pour la plupart des usages
  // On utilise une solution simple et sûre :
  return s.slice(0, -1)
}

function toggleKeyboard() {
  showKeyboard.value = !showKeyboard.value

  if (showKeyboard.value) {
    // Si on affiche le clavier, on le monte après l’apparition du DOM
    initKeyboard()
  } else {
    // Si on le masque, on le détruit (optionnel)
    document.querySelector('.simple-keyboard')?.replaceChildren()
  }
}


async function analyse(query = null) {
  // Si on reçoit un Event (KeyboardEvent / MouseEvent), on l'ignore
  if (query instanceof Event) query = null

  // Si on reçoit autre chose que string (ex. undefined), on prend text.value
  const mot = (typeof query === 'string' ? query : String(text.value || '')).trim()
  if (!mot) return

  // même logique que tu avais
  if (showResult.value) {
    showResult.value = false
    await new Promise(resolve => setTimeout(resolve, 400))
  }

  loading.value = true
  error.value = null
  result.value = null

  try {
    const res = await fetch(`http://127.0.0.1:8000/analyse?text=${encodeURIComponent(mot)}`)
    if (!res.ok) throw new Error(`Erreur ${res.status}`)
    const data = await res.json()
    console.log('✅ Données reçues:', data)
    result.value = data.result
    setTimeout(() => { showResult.value = true }, 200)
  } catch (err) {
    console.error('❌ Erreur de fetch:', err)
    error.value = 'Une erreur est survenue.'
  } finally {
    loading.value = false
  }
}

// 🔤 Nettoyage et découpage des exemples
function parseExemple(exemple) {
  const clean = exemple.replace(/\s+/g, ' ').trim()
  const parts = clean.split(' ')
  return { hanja: parts[0], korean: parts[1], meaning: parts.slice(2).join(' ') }
}

// 🚀 Relance l’analyse quand on clique sur un mot coréen
function rechercherMot(koreanWord) {
  text.value = koreanWord
  analyse(koreanWord)
}
</script>

<template>
  <div style="max-width:700px;margin:2rem auto;font-family:sans-serif;">
    <h1>🌊 Get the hanja</h1>

    <input
      v-model="text"
      @keyup.enter="analyse"
      placeholder="Write a Korean word with Hanja..."
      style="width:100%;padding:0.5rem;margin-bottom:1rem;"
    />

    <!-- Bouton pour afficher / masquer le clavier -->
    <button @click="toggleKeyboard" style="padding:0.5rem 1rem;margin-bottom:1rem;">
      {{ showKeyboard ? "Masquer le clavier coréen" : "Afficher le clavier coréen" }}
    </button>

    <!-- Clavier coréen -->
    <transition name="fade">
      <div v-show="showKeyboard" class="simple-keyboard"></div>
    </transition>


    <button @click="analyse" :disabled="loading" style="padding:0.5rem 1rem;">
      {{ loading ? 'Loading...' : 'Search' }}
    </button>
    

    <p v-if="error" style="color:red;margin-top:1rem;">{{ error }}</p>

    <!-- Loader -->
    <div v-if="loading" class="spinner-container">
      <div class="spinner"></div>
      <p>Loading ...</p>
    </div>

    <!-- Résultat -->
    <transition name="fade" mode="out-in">
      <div v-if="showResult && result" key="result" style="margin-top:2rem;">
        <h2>Résultat pour : <span style="color:#0077cc;">{{ result.mot }}</span></h2>
        <p><strong>Hanja :</strong> {{ result.hanja }}</p>

        <div v-for="detail in result.details" :key="detail.caractere" class="card">
          <h3>{{ detail.caractere }}</h3>
          <p><em>{{ detail.definition }}</em></p>

          <ul>
            <li
              v-for="(exemple, i) in detail.exemples"
              :key="i"
            >
              <strong>{{ parseExemple(exemple).hanja }}</strong>
              <!-- 🔗 le mot coréen devient un lien -->
              <a
                href="#"
                @click.prevent="rechercherMot(parseExemple(exemple).korean)"
                style="text-decoration:underline;cursor:pointer;"
              >
                {{ parseExemple(exemple).korean }}
              </a>
              — {{ parseExemple(exemple).meaning }}
            </li>
          </ul>
        </div>
      </div>
    </transition>
  </div>
</template>

<style>
.card {
  background: #000000;
  margin: 10px 0;
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Spinner animé */
.spinner-container {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 1rem;
  font-size: 1.1rem;
  color: #333;
}
.spinner {
  width: 22px;
  height: 22px;
  border: 3px solid #ccc;
  border-top: 3px solid #0077cc;
  border-radius: 50%;
  animation: spin 0.9s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Animation fade */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.simple-keyboard {
  margin-top: 1rem;
  background: #f5f5f5;
  border-radius: 8px;
  padding: 0.5rem;
}
.simple-keyboard .hg-button {
  color: black !important;
  font-size: 18px;
  min-width: 30px;
}

/* Transition fluide */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.4s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
