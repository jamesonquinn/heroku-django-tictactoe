from tictactoe import tictactoe

@tictactoe.route 
@tictactoe.route('/hello')
def hello():
    return "Hello tictactoe!"