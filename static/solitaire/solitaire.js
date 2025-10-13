document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.card[draggable=true]');
    const piles = document.querySelectorAll('.tableau-pile, .foundation-pile');

    cards.forEach(card => {
        card.addEventListener('dragstart', dragStart);
    });

    piles.forEach(pile => {
        pile.addEventListener('dragover', dragOver);
        pile.addEventListener('drop', drop);
    });

    function dragStart(e) {
        e.dataTransfer.setData('text/plain', e.target.dataset.cardInfo);
    }

    function dragOver(e) {
        e.preventDefault();
    }

    function drop(e) {
        e.preventDefault();
        const cardInfo = e.dataTransfer.getData('text');
        const toPile = e.currentTarget.dataset.pileInfo;

        const form = document.getElementById('move-card-form');
        form.querySelector('input[name=card_info]').value = cardInfo;
        form.querySelector('input[name=to_pile]').value = toPile;
        form.submit();
    }
});
