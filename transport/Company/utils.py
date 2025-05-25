
def convert(date):
    """
    Prend deux timestamps (en secondes) et renvoie une liste [heures, minutes, secondes]
    représentant la durée entre les deux.
    """
    heures = int(date // 3600)
    minutes = int((date % 3600) // 60)
    secondes = int(date % 60)
    return (heures, minutes, secondes)