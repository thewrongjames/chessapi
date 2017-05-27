from ..utilities import iterable_to_discrete_vector
from ..discrete_vector import DiscreteVector
from ..constants import COLOURS, BOARD_WIDTH, BOARD_HEIGHT


class Piece:
    _base_moves = []

    def __init__(self, position, colour, game):
        position = iterable_to_discrete_vector(position)
        if not isinstance(position, DiscreteVector):
            print(position)
            raise TypeError(
                'position must be a DiscreteVector or an iterable containing '
                'two integers'
            )
        if not colour in COLOURS:
            raise ValueError('colour must be in {}'.format(str(COLOURS)))
        # Note, game is not validated because it makes imports difficult to do
        # that.
        self.position = position
        self.colour = colour
        self.game = game

    @property
    def current_moves(self):
        return self.get_standardly_valid_moves(
            self.get_specifically_valid_moves(self._base_moves)
        )

    def get_standardly_valid_moves(self, moves_to_validate):
        """
        This function returns a modified version of moves_to_validate that only
        contains valid moves. However, this is only insofar as the generic
        restrictions that affect all pieces. If the ends on the board, any
        piece that is there has a different colour than this piece and there
        are no pieces in the way (or it is a knight), this will say it is valid,
        otherwise, it will say it is not.
        """
        valid_moves = []

        def is_valid(move):
            move = iterable_to_discrete_vector(move)
            if not isinstance(move, DiscreteVector):
                raise TypeError(
                    'move must be a DiscreteVector or an iterable with two '
                    'integers in it'
                )
            final_position = self.position + move
            piece_to_take = self.game.piece_at_position(final_position)
            colour_of_piece_to_take = None if piece_to_take is None else \
                piece_to_take.colour

            if (
                    0 <= final_position.x < BOARD_WIDTH and
                    0 <= final_position.y < BOARD_HEIGHT and
                    self.colour != colour_of_piece_to_take and
                    self.can_move_along_path(move)
            ):
                return True
            return False

        try:
            for move in moves_to_validate:
                if is_valid(move):
                    valid_moves.append(move)
        except TypeError:
            raise TypeError('moves_to_validate must be iterable')

        return valid_moves

    def get_specifically_valid_moves(self, moves_to_validate):
        # If there are no specific restrictions or moves to add, just return
        # what is passed.
        return moves_to_validate.copy()

    def can_move_along_path(self, move):
        # The knight overrides this, so, we don't need to account for it here.
        move = iterable_to_discrete_vector(move)
        if not isinstance(move, DiscreteVector):
            raise TypeError(
                'move must be a DiscreteVector or an iterable '
                'with two items in it'
            )

        number_of_squares_moved_through = (
            abs(move.x) if abs(move.x) > abs(move.y) else abs(move.y)
        )
        single_square_move = move / number_of_squares_moved_through
        path_is_blocked = False
        position_to_check = self.position.copy() + single_square_move
        # We don't need to check if the square one square away is blocked.
        while position_to_check != self.position + move:
            if self.game.piece_at_position(position_to_check) is not None:
                path_is_blocked = True
                break
            position_to_check += single_square_move

        return not path_is_blocked


    def make_move(self, move):
        """
        This function just sets the pieces position to be its current position
        plus the move. There is no validation here. Use current_moves to see a
        list of the moves that chess allows to be made from this pieces
        position. Using this function on non valid moves may provide unexpected
        results.
        """
        move = iterable_to_discrete_vector(move)
        if not isinstance(move, DiscreteVector):
            raise TypeError(
                'move must be a DiscreteVector or an iterable with two items '
                'in it'
            )

        self.position += move