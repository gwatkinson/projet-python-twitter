## Fonctions auxiliaires

# Affichage du progrès
def progressBar(current, total, prefix=None, file=None, total_file=None, barLength=20):
    """ Affiche une barre de progrès """
    percent = float(current) * 100 / total
    arrow = "-" * int(percent / 100 * barLength - 1) + ">"
    spaces = " " * (barLength - len(arrow) - 1)
    if prefix is None:
        prefix = (
            f"File {file}/{total_file}"
            if file is not None and total_file is not None
            else "Progress"
        )
    print(f"{prefix}: [{arrow}{spaces}] {percent:.0f} %", end="\r")


## Les erreurs du projet


class CredentialsType(Exception):
    """Erreur à lever si `credentials` n'est pas un dictionnaire."""

    def __init__(self, type, message="'credentials' doit être un dictionnaire, pas un"):
        self.type = type
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} {str(self.type)}"


class MissingKey(Exception):
    """Erreur à lever s'il manque des clés dans le dictionnaire."""

    def __init__(
        self, missing_keys, message="Il manque des clés dans le dictionnaire."
    ):
        self.missing_keys = missing_keys
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} -> {str(self.missing_keys)}"


class CredentialsKeyType(Exception):
    """Erreur à lever si les clés ne sont pas des `str`."""

    def __init__(self, wrong_keys, message="doivent être des strings."):
        self.wrong_keys = wrong_keys
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{str(self.wrong_keys)} {self.message}"


class CredentialsClassType(Exception):
    """Erreur à lever si `credentials` n'est pas une instance de `credentials_class`."""

    def __init__(
        self,
        type,
        message="'credentials' doit être une instance de 'credentials_class', pas un",
    ):
        self.type = type
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} {str(self.type)}"


class WordType(Exception):
    """Erreur à lever si les mots de la liste de mots à suivre ne sont pas des `str`."""

    def __init__(self, wrong_words, message="doivent être des strings."):
        self.wrong_words = wrong_words
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{str(self.wrong_words)} {self.message}"