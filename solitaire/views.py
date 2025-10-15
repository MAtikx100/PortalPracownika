from django.shortcuts import render, redirect
from .game import Game, Card

def solitaire_view(request):
    if 'game' not in request.session or request.POST.get('action') == 'new_game':
        game = Game()
        request.session['game'] = game
    else:
        game = request.session['game']

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'draw_card':
            game.draw_from_stock()
        elif action == 'move_card':
            card_info = request.POST.get('card_info').split('.')
            to_pile_info = request.POST.get('to_pile').split('.')

            from_pile_type = card_info[0]
            from_pile_index = int(card_info[1])

            if from_pile_type == 'tableau':
                from_pile = game.tableau[from_pile_index]
                card_index = int(card_info[2])
                card = from_pile[card_index]
            else: # talon
                from_pile = game.talon
                card = from_pile[-1]

            to_pile_type = to_pile_info[0]
            to_pile_index = int(to_pile_info[1])

            if to_pile_type == 'tableau':
                to_pile = game.tableau[to_pile_index]
            else: # foundation
                to_pile = game.foundations[to_pile_index]

            game.move_card(from_pile, to_pile, card)

        request.session['game'] = game
        return redirect('solitaire')

    return render(request, 'solitaire/solitaire.html', {'game': game})
