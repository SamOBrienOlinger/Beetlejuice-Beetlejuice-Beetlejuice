const FIRST_PHRASE = document.getElementById("firstResult");
const SECOND_PHRASE = document.getElementById("secondResult");
const THIRD_PHRASE = document.getElementById("thirdResult");
// JavaScript to dynamically update the copyright year
const currentYear = new Date().getFullYear();
const copyrightYear = document.getElementById('copyrightYear');
if (copyrightYear) {
  copyrightYear.textContent = currentYear;
}

// **** ELEMENT DISABLE CODE ****
const NAME_ELEMENT = document.getElementById("name");

let phraseListOne = [
  "shall forever",
  "is cursed to",
  "will endlessly",
  "is fated to",
  "shall eternally",
  "is doomed to",
  "will repeatedly",
  "has been chosen to",
  "is condemned to",
  "will henceforth",
];
let phraseListTwo = [
  "endure",
  "suffer through",
  "face",
  "confront",
  "be haunted by",
  "be tormented by",
  "be plagued by",
  "be surrounded by",
  "be trapped with",
];
let phraseListThree = [
  "a mountain of Beetlejuice's poop",
  "buckets of Beetlejuice's spittle",
  "a lake of boiling Beetlejuice — whatever that means; use your imagination",
  "rotting corpses with far too many teeth",
  "a mountain of stale candy corn",
  "buckets of sinister sweets",
  "a lake of witches' brew",
  "rotten pumpkins carved in their own likenesses",
  "eerie whispers beneath the moonlight",
  "spectral footsteps in the dark",
  "a relentless barrage of spooktacular puns",
  "cauldrons bubbling with enchanted brews",
  "ghosts and goblins at the doorstep",
  "skeletons dancing to \"The Monster Mash\"",
  "sweets that somebody else has sucked and spat out",
  "shrieking Halloween masks",
  "swarms of creepy-crawlies",
  "tap-dancing spiders",
  "invisible sandworms",
  "friends and family dancing to \"Day-O (The Banana Boat Song)\" with unnerving enthusiasm",
];

let phraseListIndexMap = [phraseListOne, phraseListTwo, phraseListThree];
let phraseElementIndexMap = [FIRST_PHRASE, SECOND_PHRASE, THIRD_PHRASE];

const COMMON_WORDS = new Set([
  "a", "an", "and", "at", "be", "been", "by", "for", "has", "in", "is",
  "of", "on", "shall", "that", "the", "their", "through", "to", "will", "with",
]);

function normalizeWord(word) {
  let normalizedWord = word
    .toLowerCase()
    .replace(/['’]s$/, "")
    .replace(/[^a-z0-9]/g, "");

  if (normalizedWord.endsWith("ly") && normalizedWord.length > 5) {
    normalizedWord = normalizedWord.slice(0, -2);
  }

  return normalizedWord;
}

function getMeaningfulWords(phrase) {
  return phrase
    .split(/\s+/)
    .map(normalizeWord)
    .filter((word) => word && !COMMON_WORDS.has(word));
}

function repeatsEarlierWord(candidate, index) {
  const earlierWords = new Set(
    phraseElementIndexMap
      .slice(0, index)
      .flatMap((element) => getMeaningfulWords(element.textContent))
  );

  return getMeaningfulWords(candidate).some((word) => earlierWords.has(word));
}

let generateCurse = function (e) {
  if (!checkName()) {
    return;
  }

  let buttonIndex = parseInt(e.target.dataset.index) - 1;
  generateText(buttonIndex);

  // **** ELEMENT DISABLE CODE ****
  CURSE_BUTTONS.forEach((button) => (button.classList.add("disabled")));

  if (buttonIndex != 2) {
    CURSE_BUTTONS[buttonIndex + 1].classList.remove("disabled");
    } else {
      buttonFinal.classList.remove("disabled");
    }
};

// **** GENERATE RANDOM PHRASE FROM ARRAYS CODE ****
const CURSE_BUTTONS = Array.from(document.getElementsByClassName("curse-button"));
CURSE_BUTTONS.forEach((button) => button.addEventListener("click", generateCurse)
);

let generateText = function (index) {
  let phraseList = phraseListIndexMap[index];
  let compatiblePhrases = phraseList.filter(
    (phrase) => !repeatsEarlierWord(phrase, index)
  );
  let phrasePool = compatiblePhrases.length > 0 ? compatiblePhrases : phraseList;
  let phrase = phrasePool[Math.floor(Math.random() * phrasePool.length)];

  let phraseElement = phraseElementIndexMap[index];
  phraseElement.innerHTML = phrase;
};

// **** ELEMENT DISABLE CODE ****
if (NAME_ELEMENT && CURSE_BUTTONS[0]) {
  NAME_ELEMENT.addEventListener("focusout", () =>
    CURSE_BUTTONS[0].classList.remove("disabled")
  );
}

// **** GENERATE FULL HEX CODE ****

const buttonFinal = document.getElementById("finalButton");
if (buttonFinal) {
  buttonFinal.addEventListener("click", () => {
    if (checkName() && checkButtons()) {
// Function to display head spinner when finalButton is clicked for a set amount of time
      genSpin();
      genHex();
    }
  });
}


function showCurseAndBeetlejuice() {

  const headspinDiv = document.getElementById('headspin');
  const jumpingFooter = document.getElementById("foot");
  const curseAndBeetlejuiceDiv = document.getElementById('curse-and-beetlejuice');

  jumpingFooter.style.display = "block";
  curseAndBeetlejuiceDiv.style.display = 'block';
  headspinDiv.style.display = 'none';
}

function genSpin() {
  const notPhussy = document.getElementById("phussy");
  const jumpingFooter = document.getElementById("foot");
  const headspinDiv = document.getElementById('headspin');

  jumpingFooter.style.display = "none";
  notPhussy.style.display = "none";
  headspinDiv.style.display = 'block';

  const timeoutDelay = 3000; // delay in ms
  setTimeout(showCurseAndBeetlejuice, timeoutDelay);
}

// **** ENSURE USER INPUTS TEXT TO START HEX CODE ****
function checkName() {
  if (document.getElementById("name").value !== "") {
    document.getElementById("name").placeholder = "";
    return true;
  } else {
    document.getElementById("name").placeholder = "Beetlejuice needs a victim's name!";
    return false;
}}

// **** ENSURE USER HAS PRESSED ALL BUTTONS **** //
function checkButtons() {
  if ((document.getElementById("firstResult").innerHTML == ``) || (
    document.getElementById("secondResult").innerHTML == ``) || (
    document.getElementById("thirdResult").innerHTML == ``)) {
      document.getElementById("finalButton").innerHTML = `<b id="fullPhrase" class="fw-bold fs-3">Complete every curse step first!</b>`;
      return false;
  } else {
      document.getElementById("finalButton").innerHTML = `<b id="fullPhrase" class="fw-bold fs-3">Click here — it's showtime!</b>`;
      return true;
  }
}

// **** BACK TO TOP AND RELOAD PAGE CODE ****
const refreshPage = document.getElementById("refresh");
if (refreshPage) {
  refreshPage.addEventListener("click", () => {
    document.location.reload();
  });
}

function genHex() {
  let finalPhrase = document.getElementById("finalResult");
  let name = document.getElementById("name").value;
  let phrase = `${FIRST_PHRASE.innerHTML} ${SECOND_PHRASE.innerHTML} ${THIRD_PHRASE.innerHTML}`;
  finalPhrase.innerHTML = name + " " + phrase + "!";
}

// Function for playing scary sounds
function playSound() {
    const sound = new Audio(''); //Insert path to audio file here
    sound.play();
}
//Click event listener for certain classes to play scary sound, target class can be changed.
document.addEventListener('click', function (event) {
    if (event.target.classList.contains('scary-sound')) {
      playSound();
    }
  });
