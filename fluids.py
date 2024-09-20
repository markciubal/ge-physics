def pressure(area, force):
    return force / area

def pressureInLiquid(density, depth, patm=101325):
    return density * 9.80 * depth