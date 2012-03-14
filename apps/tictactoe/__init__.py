from lazyblueprint import LazyBlueprint
from app import auth, db, app, mail

tictactoe = LazyBlueprint('simple_page', __name__,
                        template_folder='templates')
