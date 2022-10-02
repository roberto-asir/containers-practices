from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import games_counter
import random
import logging
import os
import json
from django.forms.models import model_to_dict

import logging
import logging.config  # needed when logging_config doesn't start with logging.config
from copy import copy


# Create your views here.
def index(request):
    # try:
    #     games_state = games_counter.objects.get(pk=1)
    # except:
    #     games_state = "Circulen, no hay nada que ver aquí."


    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('mydjango.server')


    

    sql_banner = True
    if 'POSTGRES_HOST' in os.environ:
        sql_banner = False

    try:
        games_state = games_counter.objects.last()
    except:
        games_state = games_counter()
        games_state.player = 0
        games_state.pc = 0
        games_state.save()

    games_state_dict = model_to_dict(games_state)
    logger.info(games_state_dict)

    game = {
        'winner': '',
        'player': 0,
        'ia': 0,
        'player_choice': ''
    }


    if (request.META['REQUEST_METHOD'] == "POST"):
        game['player_choice'] = request.POST.__getitem__('bet')
        game['player'] = int(request.POST.__getitem__('quantity'))
        # ia elige respuesta
        options = [0,1,2,3,4,5]
        game['ia'] = random.choice(options)

        # comprobar respuestas
        result = 'odd'
        discarted = 'even'
        if (game['ia'] + game['player']) % 2 == 0:
            result = 'even'
            discarted = 'odd'
        
        

        # actualizar games_state        
        # asignar valor a winner (player, skynet)


        if game['player_choice'] == discarted:
            game['winner'] = 'IA'
            games_state.pc = games_state.pc + 1
        if game['player_choice'] == result:
            game['winner'] = 'You'
            games_state.player = games_state.player + 1
        if game['player_choice'] == "none":
            game['nochoice'] = True

        result = json.dumps(game)
        logger.info(result)

        # salvar estado
        games_state.save()





    template = loader.get_template('games/index.html')
    context = {
        'score': games_state,
        'game': game,
        'sql_banner': sql_banner
    }
    return HttpResponse(template.render(context, request))

