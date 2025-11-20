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
const showHelp = ref(false)

// 🔧 Configuration de l'API
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

try {
    const response = await fetch(`${API_URL}/api/analyse?text=${encodeURIComponent(text.value)}`)
    
    if (!response.ok) {
      throw new Error(`Erreur API: ${response.status}`)
    }
    
    const data = await response.json()
    result.value = data.result
    showResult.value = true
    console.log('Résultat:', data)
    
  } catch (err) {
    console.error('Erreur lors de l\'appel API:', err)
    error.value = 'Impossible de contacter le serveur. Vérifiez votre connexion.'
  } finally {
    loading.value = false
  }


const message = `🇰🇷 Why Knowing Hanja Is Important for Learning Korean <br>
Learning Hanja (Chinese characters used in Korean) is not mandatory today, but it offers major advantages for anyone who wants to understand Korean deeply.<br>
1. Better Vocabulary Understanding Over 60% of Korean words come from Hanja.Knowing the characters helps you understand the root meaning of many words, even if you’ve never seen them before.For example:<br>
* 학 (學) = study → 학교 (school), 학생 (student), 학습 (learning)<br>
2. Clearer Distinction Between Similar Words Many Korean words sound identical but have different meanings.Hanja helps you distinguish homonyms instantly.Example:<br>
* 사과 (apple) = 沙果<br>
* 사과 (apology) = 謝過<br>
3. Faster Vocabulary Acquisition Once you know a few common Hanja, you can guess the meanings of new words simply by recognizing the components.This makes learning more logical and less about memorization.<br>
4. Improved Reading Comprehension In newspapers, academic texts, and legal documents, many terms are based on Hanja.Knowing them helps you understand formal and technical vocabulary more easily.<br>
5. Cultural and Historical Insight Hanja connects Korean to its historical roots and traditional literature.Understanding it gives you deeper insight into Korean culture, names, idioms, and expressions.<br>`

const messageWithBreaks = message

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
        "ㅁ ㄴ ㅇ ㄹ ㅎ ㅗ ㅓ ㅏ ㅣ ㅐ ㅔ",
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
    updateText()
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


function removeLastGrapheme(s) {
  if (!s) return ''
  if (s.slice(-1) === ' ') return s.slice(0, -1)
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
    result.value = data.result
    setTimeout(() => { showResult.value = true }, 200)
  } catch (err) {
    error.value = 'Une erreur est survenue.'
  } finally {
    loading.value = false
  }
}

function parseExemple(exemple) {
  const clean = exemple.replace(/\s+/g, ' ').trim()
  const parts = clean.split(' ')
  return { hanja: parts[0], korean: parts[1], meaning: parts.slice(2).join(' ') }
}

function rechercherMot(koreanWord) {
  text.value = koreanWord
  analyse(koreanWord)
}

</script>

<template>

<div class="help-container">
  <div 
    class="help-icon"
    @click="showHelp = !showHelp"
  >
    ?
  </div>

  <!-- Transition pour l'animation -->
  <transition name="tooltip-fade">
    <div v-if="showHelp" class="tooltip" v-html="messageWithBreaks"></div>
  </transition>
</div>

  <div style="width:85vw;margin:0;padding:2rem;font-family:sans-serif;box-sizing:border-box;position:relative;left:0%;right:0%">
              <h1>🇰🇷 Get the hanja</h1>

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
        <h2>Résultat pour : <span style="color:#0077cc;">{{ result.mot }}</span>  (<span style="color: #0077cc;">{{ result.translation }}</span>)</h2>
        <p><strong>Hanja :</strong> {{ result.hanja }}</p>


        <div class="cards-container">
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


      </div>
    </transition>
</div>
</template>

<style>
.help-container {
  position: fixed;
  top: 10px;
  left: 10px;
  z-index: 9999;
}

.help-icon {
  background: gray;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  text-align: center;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.tooltip {
  position: fixed;
  top: 40px;
  left: 0;
  background: black;
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 14px;
  z-index: 9999;
  white-space: normal;
  max-width: 1200px;
  width: auto;
  word-wrap: break-word;
}

/* Animation fade + slide */
.tooltip-fade-enter-active,
.tooltip-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.tooltip-fade-enter-from,
.tooltip-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.tooltip-fade-enter-to,
.tooltip-fade-leave-from {
  opacity: 1;
  transform: translateY(0);
}


/* Conteneur des cards */
.cards-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

/* Sur écran large → 2 colonnes */
@media (min-width: 900px) {
  .cards-container {
    grid-template-columns: repeat(3, 1fr);
    width: 100%;
  }
}

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

#app {
  width: 100%;
  min-width: 0;
}

</style>
