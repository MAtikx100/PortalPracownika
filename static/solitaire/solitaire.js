document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const stockPileEl = document.querySelector('.stock-pile');
    const talonPileEl = document.querySelector('.talon-pile');
    const foundationPilesEl = document.querySelectorAll('.foundation-pile');
    const tableauPilesEl = document.querySelectorAll('.tableau-pile');
    const newGameButton = document.getElementById('new-game-button');

    // Game state
    let stock = [];
    let talon = [];
    let foundations = [[], [], [], []];
    let tableau = [[], [], [], [], [], [], []];
    let dragged = { card: null, sourcePile: null, element: null };

    // --- Game Logic ---
    function createDeck() {
        const suits = { '♥': 'red', '♦': 'red', '♣': 'black', '♠': 'black' };
        const ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'];
        const deck = [];
        for (const suit in suits) {
            for (let i = 0; i < ranks.length; i++) {
                deck.push({ suit, rank: ranks[i], color: suits[suit], value: i + 1, isFaceUp: false });
            }
        }
        return deck;
    }

    function shuffle(deck) {
        for (let i = deck.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [deck[i], deck[j]] = [deck[j], deck[i]];
        }
        return deck;
    }

    function deal() {
        const deck = shuffle(createDeck());
        stock = deck;
        talon = [];
        foundations = [[], [], [], []];
        tableau = [[], [], [], [], [], [], []];

        for (let i = 0; i < 7; i++) {
            for (let j = i; j < 7; j++) {
                tableau[j].push(stock.pop());
            }
        }

        tableau.forEach(pile => {
            if (pile.length > 0) {
                pile[pile.length - 1].isFaceUp = true;
            }
        });
    }

    // --- Rendering ---
    function render() {
        // Clear all piles
        [...tableauPilesEl, ...foundationPilesEl, stockPileEl, talonPileEl].forEach(p => p.innerHTML = '');

        // Render Tableau
        tableau.forEach((pile, i) => {
            pile.forEach((card, j) => {
                const cardEl = createCardElement(card);
                cardEl.style.top = `${j * 30}px`;
                cardEl.dataset.pile = 'tableau';
                cardEl.dataset.pileIndex = i;
                cardEl.dataset.cardIndex = j;
                tableauPilesEl[i].appendChild(cardEl);
            });
        });

        // Render Foundations
        foundations.forEach((pile, i) => {
            if (pile.length > 0) {
                const card = pile[pile.length - 1];
                const cardEl = createCardElement(card);
                cardEl.dataset.pile = 'foundation';
                cardEl.dataset.pileIndex = i;
                cardEl.dataset.cardIndex = pile.length - 1;
                foundationPilesEl[i].appendChild(cardEl);
            }
        });

        // Render Stock & Talon
        if (stock.length > 0) {
            const cardEl = createCardElement({ isFaceUp: false });
            stockPileEl.appendChild(cardEl);
        } else {
            stockPileEl.classList.add('empty-stock');
            stockPileEl.innerHTML = '<span>&#x21BA;</span>';
        }

        if (talon.length > 0) {
            const card = talon[talon.length - 1];
            const cardEl = createCardElement(card);
            cardEl.dataset.pile = 'talon';
            talonPileEl.appendChild(cardEl);
        }
    }

    function createCardElement(card) {
        const el = document.createElement('div');
        el.classList.add('card');
        if (card.isFaceUp) {
            el.style.color = card.color;
            el.innerHTML = `<span>${card.rank}</span><span>${card.suit}</span>`;
            el.draggable = true;
        } else {
            el.classList.add('face-down');
        }
        return el;
    }

    // --- Event Handlers ---
    function handleStockClick() {
        if (stock.length > 0) {
            talon.push(...stock.splice(-3).map(c => ({ ...c, isFaceUp: true })));
        } else if (talon.length > 0) {
            stock = talon.reverse().map(c => ({ ...c, isFaceUp: false }));
            talon = [];
        }
        render();
    }

    function handleDragStart(e) {
        if (!e.target.classList.contains('card')) return;
        e.target.classList.add('dragging');
        dragged.element = e.target;
        const { pile, pileIndex, cardIndex } = e.target.dataset;
        
        if (pile === 'tableau') {
            dragged.sourcePile = tableau[pileIndex];
            dragged.card = dragged.sourcePile[cardIndex];
        } else if (pile === 'talon') {
            dragged.sourcePile = talon;
            dragged.card = talon[talon.length - 1];
        }
    }

    function handleDragEnd(e) {
        if (dragged.element) {
            dragged.element.classList.remove('dragging');
        }
        dragged = { card: null, sourcePile: null, element: null };
    }

    function handleDrop(e) {
        e.preventDefault();
        if (!dragged.card) return;

        const targetPileEl = e.currentTarget;
        const toPileType = targetPileEl.classList.contains('tableau-pile') ? 'tableau' : 'foundation';
        const toPileIndex = targetPileEl.dataset.pileIndex;
        const toPile = toPileType === 'tableau' ? tableau[toPileIndex] : foundations[toPileIndex];

        if (isValidMove(dragged.card, dragged.sourcePile, toPile, toPileType)) {
            const cardIndex = dragged.sourcePile.indexOf(dragged.card);
            const cardsToMove = dragged.sourcePile.splice(cardIndex);
            toPile.push(...cardsToMove);

            // Flip card in source tableau pile
            if (Array.isArray(dragged.sourcePile) && dragged.sourcePile.length > 0) {
                dragged.sourcePile[dragged.sourcePile.length - 1].isFaceUp = true;
            }

            render();
            checkWinCondition();
        }
    }

    // --- Move Validation ---
    function isValidMove(card, fromPile, toPile, toPileType) {
        if (toPileType === 'foundation') {
            const topCard = toPile.length > 0 ? toPile[toPile.length - 1] : null;
            if (topCard) {
                return card.suit === topCard.suit && card.value === topCard.value + 1;
            } else {
                return card.rank === 'A';
            }
        } else if (toPileType === 'tableau') {
            const topCard = toPile.length > 0 ? toPile[toPile.length - 1] : null;
            if (topCard) {
                return card.color !== topCard.color && card.value === topCard.value - 1;
            } else {
                return card.rank === 'K';
            }
        }
        return false;
    }

    function checkWinCondition() {
        if (foundations.every(p => p.length === 13)) {
            setTimeout(() => alert('You Win!'), 100);
        }
    }

    // --- Initial Setup ---
    function init() {
        deal();
        render();

        stockPileEl.addEventListener('click', handleStockClick);
        newGameButton.addEventListener('click', init);

        document.addEventListener('dragstart', handleDragStart);
        document.addEventListener('dragend', handleDragEnd);
        document.querySelectorAll('.tableau-pile, .foundation-pile').forEach(pile => {
            pile.addEventListener('dragover', e => e.preventDefault());
            pile.addEventListener('drop', handleDrop);
        });
    }

    init();
});
