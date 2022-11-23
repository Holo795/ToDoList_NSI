from flask import *  # for flash messages

from bdd.bdd import Accounts  # Accounts database gestion
import bcrypt  # for password hashing


class AccountsManager:
    """Classe pour gérer les comptes"""
    def __init__(self):
        """Constructeur"""
        self.accounts = Accounts("todo.sqlite")

    def login(self, request):
        """Connecte un utilisateur"""
        username = request.form.get("username")
        password = request.form.get("password")
        if account := self.accounts.get_account(username):
            account = account[0]
            if bcrypt.checkpw(password.encode('utf8'), account[2].encode('utf8')):
                session["username"] = username
                return redirect(url_for("accueillir"))
            else:
                flash("Mot de passe incorrect", "error")
        else:
            flash("Cet utilisateur n'existe pas", "error")
        return redirect(url_for("accueillir"))

    def logout(self):
        """Déconnecte un utilisateur"""
        session.pop("username", None)
        return redirect(url_for("accueillir"))

    def register(self, request):
        """Enregistre un utilisateur"""
        username = request.form.get("username")
        password = request.form.get("password")
        if self.accounts.get_account(username):
            flash("Cet utilisateur existe déjà", "error")
        else:
            self.accounts.add_account(username, bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt()).decode('utf8'))
            flash("Compte créé", "success")
        return redirect(url_for("accueillir"))
