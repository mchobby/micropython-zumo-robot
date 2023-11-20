""" maze_simplify.py - alternate way to simplify path by using a pure
   					pythonic approach. By being called only once after the
					maze exploration.
"""

SUBS = { "RBL":"B", "LBR":"B", "SBL":"R", "LBS":"R", "LBL":"S", "RBR":"S" }

def simplify( path ):
    path_str = ''.join( path ) # List to String

    print( 'Start path: %s' % path_str )
    try_again = True # Enter the loop
    while try_again:
        try_again = False
        for rpl_from, rpl_by in SUBS.items():
            if rpl_from in path_str:
                path_str = path_str.replace( rpl_from, rpl_by )
                print( rpl_from, "->", rpl_by , "| path=", path_str )

                try_again = True # We should make a new round of replacement
                break # break the for loop
    # No more simplification possible
    # --> return the result
    return list( path_str )

chemin = ['L', 'S', 'B', 'L', 'B', 'L', 'L', 'B', 'L']
# chemin = list( "RLBLLLLSRBLLLLRR" )
# chemin = list( "rlrllslbrllbsllsrbllr".upper() )
#chemin = list( "rlrlllblbsrrllr".upper() )
print( "Results is", simplify(chemin) )
