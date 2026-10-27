import math

def mmc_metricas(lambda_, mu, c):
    """Fórmulas M/M/c para validar el motor DES."""
    rho = lambda_ / (c * mu)
    if rho >= 1:
        return {"estable": False, "rho": rho}

    suma = sum((lambda_/mu)**n / math.factorial(n) for n in range(c))
    ultimo = (lambda_/mu)**c / (math.factorial(c) * (1 - rho))
    p0 = 1 / (suma + ultimo)

    Lq = (p0 * (lambda_/mu)**c * rho) / (math.factorial(c) * (1 - rho)**2)
    Wq = Lq / lambda_
    L = Lq + lambda_ / mu
    W = Wq + 1 / mu

    return {"estable": True, "rho": rho, "P0": p0,
            "Lq": Lq, "Wq": Wq, "L": L, "W": W}