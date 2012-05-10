import operator
reduce(operator.mul, (3, 4, 5))

def get_forward_rates(zeroes):
    """
    zeroes is a list of zero rates where the first element
    is one year rate, 2nd is 2 year rate, etc.
    """
    forward_rates = [zeroes[0]] # the 0f1 rate is the first zero rate
    for i in range(1, len(zeroes)):
        zero_rate = zeroes[i]
        forward_rate = (((1.0 + zero_rate) ** (i+1)) / (reduce(operator.mul, [1.0 + xfy for xfy in forward_rates]))) - 1.0
        forward_rates.append(forward_rate)
    return forward_rates

   
#zeroes = [.02, .025, .03, .0337, .0369]
zeroes = [.0405, .0468, .0504, .0511, .0530]
print get_forward_rates(zeroes)        
