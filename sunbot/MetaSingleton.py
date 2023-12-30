class MetaSingleton(type):
    """Meta classe permettant de générer et centraliser l'intégralité des singletons
    de l'application."""

    # Dictionnaire privé contenant l'ensemble des singletons générés par l'application
    # à partir de cette métaclasse :
    __instances = {}

    def __call__(cls, *args, **kwargs) -> any:
        """Méthode retournant l'instance du singleton appelé"""
        # Si le singleton n'a pas encore d'instance, la créer :
        if cls not in MetaSingleton.__instances:
            MetaSingleton.__instances[cls] = super(MetaSingleton, cls).__call__(
                *args, **kwargs
            )
        return MetaSingleton.__instances[cls]
