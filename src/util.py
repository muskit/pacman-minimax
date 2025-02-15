def clip(value, lower, upper):
    """Returns `value` in the bounds [`lower`, `upper`]"""
    return lower if value < lower else upper if value > upper else value

def lerp(a, b, ratio):
    # r = clip(ratio, 0, 1)
    return a + (b-a)*ratio

def get_facing(src: tuple[int, int], dest: tuple[int, int]):
    diff = (dest[0] - src[0], dest[1] - src[1])
    if diff[0] != 0: # horizontal movement
        return 'left' if diff[0] < 0 else 'right'
    else: # vertical movement
        return 'down' if diff[1] > 0 else 'up'

## Example for how linear interpolation works ##
# What's the 50% point between 10 and 20?
# lerp(10, 20, 0.5) ---> 15
#  = 10 + (20-10)*0.5
#  = 10 + 10*0.5
#  = 10 + 5 = 15