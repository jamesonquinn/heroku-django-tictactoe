#            from django.shortcuts import get_object_or_404, 
#render_to_response, #redirect
from flask import (redirect, Response, render_template, 
                   abort, url_for, flash, request)
#from django.core.urlresolvers import #reverse=url_for
#from django.http import #HttpResponse=Response, #Http404=abort(404)
#from django.template import #RequestContext=not needed
from tictactoe import auth, app, db, mail
from flaskext.mail import Message
#from django.contrib.auth.models import #User=auth.user
#from django.contrib.auth.decorators import login_required=auth.login_required
#from django.core.mail import send_mail=see function below
import settings
#from django.contrib.sites.models import Site=used for DOMAIN
#from django.contrib import messages=flash

import json
import random

from tictactoe import tictactoe
from tictactoe.models import Game, GameMove, GameInvite
from tictactoe.lib import Player_X, Player_O
from tictactoe.forms import EmailForm

from redis import Redis
from gevent.greenlet import Greenlet


REDIS_HOST = getattr(settings, 'REDIS_HOST', 'localhost')

def send_mail(subject, body, sender, recipients, fail_silently=True):
    msg = Message(subject, recipients=recipients, sender=sender, body=body)
    mail.send(msg)
    
def _sub_listener(socketio, chan):
        red = Redis(REDIS_HOST)
        red.subscribe(chan)
        print 'subscribed on chan ', chan
        while True:
            for i in red.listen():
                socketio.send({'message': i})

@tictactoe.route("/socket.io")
def socketio():
    socketio = request.environ['socketio']

    while True:
        message = socketio.recv()

        if len(message) == 1:
            message = message[0].split(':')

            if message[0] == 'subscribe':
                print 'spawning sub listener'
                g = Greenlet.spawn(_sub_listener, socketio, message[1])

    return Response()

@tictactoe.route("/games/<int:game_id>/create_move")
@auth.login_required
def create_move(game_id):
    game = _get_game(request.user, game_id)
    if request.POST:
        move = int(request.POST['move'])
        red = Redis(REDIS_HOST)

        # get player of move
        tic_player = Player_X if game.player1 == request.user else Player_O

        GameMove(game=game, player=request.user, move=move).save()
        board = game.get_board()
        board.make_move(move, tic_player)

        # get opponent
        opponent_player = Player_O if tic_player == Player_X else Player_X
        opponent_user = game.player1 if tic_player == Player_O else game.player2

        # get computer
        computer_user = _get_computer() 
        playing_computer = computer_user in [game.player1, game.player2]

        # if game over, and not playing against computer,  send notification of move, and of game over
        winner = board.get_winner()

        if board.is_game_over():
            red.publish('%d' % request.user.id, ['game_over', game.id, winner])

            if not playing_computer:
                red.publish('%d' % opponent_user.id, ['opponent_moved', game.id, tic_player, move])
                red.publish('%d' % opponent_user.id, ['game_over', game.id, winner])
        else:
            if playing_computer:
                move, board = _create_computer_move(game, board)
                red.publish('%d' % request.user.id, ['opponent_moved', game.id, opponent_player, move])

                if board.is_game_over():
                    winner = board.get_winner()
                    red.publish('%d' % request.user.id, ['game_over', game.id, winner])
            else:
                red.publish('%d' % opponent_user.id, ['opponent_moved', game.id, tic_player, move])

    return Response()

def _create_computer_move(game, board):
    computer = auth.User.objects.get(username='bot')
    cpu = Player_X if game.player1 == computer else Player_O

    move = board.get_best_move(cpu)
    GameMove(game=game, player=computer, move=move).save()
    board.make_move(move, cpu)

    return move, board

def _get_computer():
    try:
        bot = auth.User.objects.get(username='bot')
    except auth.User.DoesNotExist:
        bot = auth.User(username='bot')
        bot.save()
    finally:
        return bot

@tictactoe.route("/games/create_computer/")
@auth.login_required
def create_computer_game():
    bot = _get_computer()

    coin_toss = random.choice([0, 1])

    if coin_toss == 0:
        game = Game(player1=request.user, player2=bot)
    else:
        game = Game(player1=bot, player2=request.user)

    game.save()

    if coin_toss == 1:
        board = game.get_board()
        move, board = _create_computer_move(game, board)

        GameMove(game=game, player=bot, move=move).save()

    return redirect('view_game', game_id=game.id)

@tictactoe.route("/games/<int:game_id>/")
@auth.login_required
def view_game(game_id, template_name='core/view_game.html'):
    bot = _get_computer()

    game = _get_game(request.user, game_id)

    player = Player_X if game.player1 == request.user else Player_O

    moves = game.gamemove_set.all().order_by('-id')

    if not moves:
        current_player = Player_X
    else:
        current_player = Player_O if moves[0].player == game.player1 else Player_X
    
    playing_computer = bot in [game.player1, game.player2]

    context = { 'game': game, 
                'board': game.get_board(), 
                'player': player, 
                'current_player': current_player,
                'playing_computer': playing_computer
              }

    return render_template(template_name, **context)

@tictactoe.route("/games/invite/<int:key>/")
@auth.login_required
def accept_invite(key):
    try:
        invite = GameInvite.objects.get(invite_key=key, is_active=True)
    except GameInvite.DoesNotExist:
        abort(404)

    if not request.user == invite.inviter:
        coin_toss = random.choice([0, 1])

        if coin_toss == 0:
            game = Game(player1=invite.inviter, player2=request.user)
        else:
            game = Game(player1=request.user, player2=invite.inviter)

        game.save()

        red = Redis(REDIS_HOST)
        red.publish('%d' % invite.inviter.id, ['game_started', game.id, str(request.user.username)])

        # No reason to keep the invites around
        invite.delete()

        return redirect('view_game', game_id=game.id)

    abort(404)

@tictactoe.route("/")
def index():
    return game_list()

@tictactoe.route("/games/")
@auth.login_required
def game_list(template_name='core/game_list.html'):
    games = Game.objects.get_by_user(request.user)[:15]

    if request.POST:
        form = EmailForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]

            if email == request.user.email:
                flash('You are not allowed to invite yourself.', 'messages.ERROR')
                form = EmailForm()
            else:
                try:
                    user = auth.User.objects.get(email=email)
                except auth.User.DoesNotExist:
                    user = None

                invite = GameInvite(inviter=request.user, is_active=True)

                if user:
                    invite.invitee = user

                invite.save()


                url = url_for('accept_invite', key=invite.invite_key)
                flash('Invite was sent!', 'messages.SUCCESS')

                if invite.invitee:
                    red = Redis(REDIS_HOST)
                    red.publish('%d' % invite.invitee.id, ['new_invite', str(request.user.username), url])

                send_mail('You are invited to play tic tac toe :)', 'Click here! %s%s' % (settings.DOMAIN, url), 'sontek@gmail.com',
                            [email], fail_silently=False)

                form = EmailForm()
    else:
        form = EmailForm()

    context = { 'games': games, 'form': form }

    return render_template(template_name, **context)

def _get_game(user, game_id):
    game = get_object_or_404(Game, pk=game_id)
    if not game.player1 == user and not game.player2 == user:
        abort(404) 

    return game

@tictactoe.route("/make_tables/")
def make_tables():
    auth.User.create_table(fail_silently=True)
    for table in (Game, GameMove, GameInvite):
        table.create_table(fail_silently=True)
    
    #if I ever come back here, would have to create admin user here...
        
    return "created!"
