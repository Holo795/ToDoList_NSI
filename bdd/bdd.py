import os
import sqlite3  # Import the SQLite3 module

# abc library for abstract base classes
from abc import abstractmethod


class Database:
    """Classe principal de la gestion de la bdd"""

    def __init__(self):
        """Constructeur"""

        folder = os.path.dirname(os.path.abspath(__file__))
        self.path = os.path.join(folder, "todo.sqlite")

        self.accounts = Accounts_Table(self.path)
        self.tasks = Tasks_Table(self.path)
        self.types = Types_Table(self.path)
        self.priorities = Priorities_Table(self.path)
        self.states = States_Table(self.path)


class BddManager:
    """Classe pour faire le lien entre la base de données SQLite et le programme"""

    def __init__(self, path: str):
        """Constructeur"""
        self.path = path
        self.connection = sqlite3.connect(path, check_same_thread=False)
        self.cursor = self.connection.cursor()

        self.create_table()

    def execute(self, request: str, parameters=None) -> list:
        """Exécute une requête SQL"""
        if parameters is None:
            self.cursor.execute(request)
        else:
            self.cursor.execute(request, parameters)
        self.connection.commit()
        return self.cursor.fetchall()

    @abstractmethod
    def create_table(self):
        """Méthode abstraite"""
        raise NotImplementedError("Méthode abstraite create_table non implémentée !")


class Tasks_Table(BddManager):
    """Classe pour gérer les tâches"""

    def __init__(self, path: str):
        """Constructeur"""
        super().__init__(path)

    def create_table(self):
        """Crée la table Taches"""
        self.execute("CREATE TABLE IF NOT EXISTS Tasks (idTask INTEGER NOT NULL UNIQUE, "
                     "idAccount INTEGER NOT NULL, "
                     "name TEXT NOT NULL CHECK (length(name) < 50), "
                     "description TEXT, "
                     "deadline_date	INTEGER NOT NULL, "
                     "success_date INTEGER, "
                     "idType INTEGER NOT NULL, "
                     "idPriority INTEGER NOT NULL, "
                     "idState INTEGER NOT NULL, "
                     "PRIMARY KEY(idTask AUTOINCREMENT), "
                     "FOREIGN KEY(idPriority) REFERENCES Priorities(idPriority), "
                     "FOREIGN KEY(idAccount) REFERENCES Accounts(idAccount), "
                     "FOREIGN KEY(idType) REFERENCES Types(idType), "
                     "FOREIGN KEY(idState) REFERENCES States(idState));")

    def get_tasks(self, idAccount) -> list:
        """Récupère les tâches d'un utilisateur"""
        return self.execute("SELECT * FROM Tasks WHERE idAccount = ? ORDER BY deadline_date ASC;", (idAccount,))

    def add_task(self, idAccount: int, name: str, description: str, deadline_date: int, idType: int,
                 idPriority: int, idState: int) -> list:
        """Ajoute une tâche à un utilisateur"""
        return self.execute("INSERT INTO Tasks (idAccount, name, description, deadline_date, success_date, idType, "
                            "idPriority, idState) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
                            (idAccount, name, description, deadline_date, None, idType, idPriority, idState))

    def edit_task(self, idTask: int, **kwargs) -> list:
        """Modifie une tâche"""
        if kwargs:
            request = "UPDATE Tasks SET "
            for key in kwargs:
                request += f"{key} = ?, "
            request = f"{request[:-2]} WHERE idTask = ?;"
            return self.execute(request, tuple(kwargs.values()) + (idTask,))
        return []

    def delete_task(self, idTask: int) -> list:
        """Supprime une tâche d'un utilisateur"""
        return self.execute("DELETE FROM Tasks WHERE idTask = ?;", (idTask,))


class Accounts_Table(BddManager):
    """Classe pour gérer les comptes dans la base de données"""

    def __init__(self, path: str):
        """Constructeur"""
        super().__init__(path)

    def create_table(self):
        """Crée la table Comptes"""
        self.execute("CREATE TABLE IF NOT EXISTS Accounts (idAccount INTEGER NOT NULL UNIQUE, "
                     "username TEXT NOT NULL CHECK(length(username) <= 20 AND length(username) > 3) UNIQUE, "
                     "password	TEXT NOT NULL ,"
                     "PRIMARY KEY(idAccount AUTOINCREMENT));")

    def add_account(self, username: str, password: str) -> list:
        """Ajoute un compte"""
        return self.execute("INSERT INTO Accounts (username, password) VALUES (?, ?);", (username, password))

    def get_account(self, username: str) -> list:
        """Récupère un compte"""
        return self.execute("SELECT * FROM Accounts WHERE username = ?;", (username,))

    def get_all_accounts(self) -> list:
        """Récupère tous les comptes"""
        return self.execute("SELECT * FROM Accounts;")

    def edit_account(self, userid: int, username=None, password=None) -> list:
        """Modifie un compte"""
        if username is not None and password is not None:
            return self.execute("UPDATE Accounts SET username = ?, password = ? WHERE idAccount = ?;",
                                (username, password, userid))
        elif username is not None:
            return self.execute("UPDATE Accounts SET username = ? WHERE idAccount = ?;", (username, userid))
        elif password is not None:
            return self.execute("UPDATE Accounts SET password = ? WHERE idAccount = ?;", (password, userid))
        return []

    def delete_account(self, username: str) -> list:
        """Supprime un compte"""
        return self.execute("DELETE FROM Accounts WHERE username = ?;", (username,))


class Types_Table(BddManager):
    """Classe pour gérer les types de tâches"""

    def __init__(self, path: str):
        """Constructeur"""
        super().__init__(path)

    def create_table(self):
        """Crée la table Types"""
        self.execute("CREATE TABLE IF NOT EXISTS Types (idType INTEGER NOT NULL UNIQUE, "
                     "name TEXT NOT NULL, "
                     "idAccount INTEGER NOT NULL, "
                     "PRIMARY KEY(idType AUTOINCREMENT));")

    def add_type(self, name: str, idAccount: int) -> list:
        """Ajoute un type de tâche"""
        return self.execute("INSERT INTO Types (name, idAccount) VALUES (?, ?);", (name, idAccount))

    def get_type(self, idType: int) -> list:
        """Récupère un type de tâche"""
        return self.execute("SELECT * FROM Types WHERE idType = ?;", (idType,))

    def get_all_types(self, idAccount: int) -> list:
        """Récupère tous les types de tâche"""
        return self.execute("SELECT * FROM Types WHERE idAccount = ?;", (idAccount,))

    def delete_type(self, idType: str) -> list:
        """Supprime un type de tâche"""
        return self.execute("DELETE FROM Types WHERE idType = ?;", (idType,))


class Priorities_Table(BddManager):
    """Classe pour gérer les priorités de tâches"""

    def __init__(self, path: str):
        """Constructeur"""
        super().__init__(path)

    def create_table(self):
        """Crée la table Priorités"""
        self.execute("CREATE TABLE IF NOT EXISTS Priorities (idPriority INTEGER NOT NULL UNIQUE, "
                     "name TEXT NOT NULL UNIQUE, "
                     "PRIMARY KEY(idPriority AUTOINCREMENT));")

        if len(self.get_all_priorities()) == 0:
            self.execute("INSERT INTO Priorities (name) VALUES ('Haute');")
            self.execute("INSERT INTO Priorities (name) VALUES ('Moyenne');")
            self.execute("INSERT INTO Priorities (name) VALUES ('Basse');")

    def add_priority(self, name: str) -> list:
        """Ajoute une priorité de tâche"""
        return self.execute("INSERT INTO Priorities (name) VALUES (?);", (name,))

    def get_priority(self, idPriority: int) -> list:
        """Récupère une priorité de tâche"""
        return self.execute("SELECT * FROM Priorities WHERE idPriority = ?;", (idPriority,))

    def get_all_priorities(self) -> list:
        """Récupère toutes les priorités de tâche"""
        return self.execute("SELECT * FROM Priorities;")

    def edit_priority(self, name: str, new_name: str) -> list:
        """Modifie une priorité de tâche"""
        return self.execute("UPDATE Priorities SET name = ? WHERE name = ?;", (new_name, name))

    def delete_priority(self, name: str) -> list:
        """Supprime une priorité de tâche"""
        return self.execute("DELETE FROM Priorities WHERE name = ?;", (name,))


class States_Table(BddManager):
    """Classe pour gérer les états de tâches"""

    def __init__(self, path: str):
        """Constructeur"""
        super().__init__(path)

    def create_table(self):
        """Crée la table États"""
        self.execute("CREATE TABLE IF NOT EXISTS States (idState INTEGER NOT NULL UNIQUE, "
                     "name TEXT NOT NULL UNIQUE, "
                     "PRIMARY KEY(idState AUTOINCREMENT));")

        if len(self.get_all_states()) == 0:
            self.add_state("En Cours")
            self.add_state("Completée")
            self.add_state("Archivée")

    def get_state(self, idState: int) -> list:
        """Récupère un état de tâche"""
        return self.execute("SELECT * FROM States WHERE idState = ?;", (idState,))

    def get_all_states(self) -> list:
        """Récupère tous les états de tâche"""
        return self.execute("SELECT * FROM States;")

    def add_state(self, name: str) -> list:
        """Ajoute un état de tâche"""
        return self.execute("INSERT INTO States (name) VALUES (?);", (name,))
