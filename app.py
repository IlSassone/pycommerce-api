from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask import request
from flask_cors import CORS
from sqlalchemy.exc import *
from sqlalchemy import select
import bcrypt
from datetime import datetime
from models import *
import os
import jwt

app = Flask(__name__)
api = Api(app)
CORS(app)

userArgs = reqparse.RequestParser()
userArgs.add_argument("email", type=str, help="manca l'email", required=True)
userArgs.add_argument("password", type=str, help="manca la password", required=True)
userArgs.add_argument("nome", type=str, help="manca il nome", required=True)
userArgs.add_argument("cognome", type=str, help="manca il cognome", required=True)
userArgs.add_argument("dataNascita", type=str, help="manca la data di nascita", required=True)
userArgs.add_argument("linkImmagine", type=str, help="Puoi mettere un immagine profilo", required=False)

loginArgs = reqparse.RequestParser()
loginArgs.add_argument("email", type=str, help="manca l'email", required=True)
loginArgs.add_argument("password", type=str, help="manca la password", required=True)


prodottoArgs = reqparse.RequestParser()
prodottoArgs.add_argument("nome", type=str, help="manca il nome", required=True)
prodottoArgs.add_argument("descrizione", type=str, help="manca la descrizione", required=True)
prodottoArgs.add_argument("prezzo", type=float, help="manca il prezzo", required=True)
prodottoArgs.add_argument("valuta", type=str, help="manca la valuta", required=True)
prodottoArgs.add_argument("linkImmagine", type=str, help="manca l'immagine", required=True)
prodottoArgs.add_argument("categoria", type=str, help="manca la categoria di appartenenza", required=True)
prodottoArgs.add_argument("token", type=str, help="manca il token di autenticazione", required=True)



venditoreArgs = reqparse.RequestParser()
venditoreArgs.add_argument("email", type=str, help="manca l'email", required=True)
venditoreArgs.add_argument("password", type=str, help="manca la password", required=True)
venditoreArgs.add_argument("nome", type=str, help="manca il nome", required=True)
venditoreArgs.add_argument("nomeAzienda", type=str, help="manca il nome azienda", required=True)
venditoreArgs.add_argument("partitaIva", type=str, help="manca il numero di partitaIva", required=True)
venditoreArgs.add_argument("indirizzo", type=str, help="manca l'indirizzo", required=True)
venditoreArgs.add_argument("provincia", type=str, help="manca la provincia", required=True)
venditoreArgs.add_argument("cap", type=str, help="manca il cap", required=True)
venditoreArgs.add_argument("cognome", type=str, help="manca il cognome", required=True)
venditoreArgs.add_argument("dataNascita", type=str, help="manca la data di nascita", required=True)
venditoreArgs.add_argument("linkImmagine", type=str, help="Puoi mettere un immagine profilo", required=False)



class ProdottiRoute(Resource):
    def get(self):
        prodotti =  db_session.query(Prodotto, Categoria, Venditore).filter(Prodotto.idCategoria==Categoria.id).filter(Prodotto.idVenditore==Venditore.id).all()
        data = []

        for o in prodotti:
            print(o)
            data.append({
                "id": o[0].id,
                "nome": o[0].nome,
                "descrizione": o[0].descrizione, 
                "prezzo": float(o[0].prezzo), 
                "valuta": o[0].valuta, 
                "linkImmagine": o[0].linkImmagine, 
                "categoria": o[1].nome,
                "nomeAzienda": o[2].nomeAzienda,
                "partitaIva": o[2].partitaIva 
            })

        return {"prodotti": data}

    def post(self):
        args = prodottoArgs.parse_args()
        token = args["token"]
        userData = jwt.decode(token,os.environ.get("JWT_SECRET") ,algorithms="HS256")
        cat = db_session.query(Categoria).filter(Categoria.nome== args["categoria"]).first()
        if cat==None:
            return {
                        "msg": "error/s",
                        "cause": "problem with input data",
                        "info": f'la categoria che stai cercando non esiste'
                    }

        print(userData["vend"])

        if(userData["vend"]==None):
            return {
                        "msg": "error/s",
                        "cause": "problem with input data",
                        "info": f'non sei loggato con un account venditore'
                    }

        
        prod = Prodotto(
            nome=args["nome"],
            descrizione = args["descrizione"],
            prezzo = args["prezzo"],
            valuta = args["valuta"],
            linkImmagine = args["linkImmagine"]
        )
        prod.idVenditore = userData["vend"]["idVenditore"]
        prod.idCategoria = cat.id
        db_session.add(prod);
        db_session.commit()
        return {
            "msg": "ok",
            "info": "prodotto aggiunto con successo"
        }


class SignUp(Resource):
    def post(self):
        args = userArgs.parse_args()
        salt = bcrypt.gensalt()
        print(args)

        for key, value in args.items():
            if(value != None and len(value)<4):
                return {
                    "msg": "error/s",
                    "cause": "missing arguments",
                    "info": f'{key} has no value'
                }

        try:
            user = Utente(
                email=args["email"], 
                password=bcrypt.hashpw(args["password"].encode("utf8"), salt),
                nome= args["nome"],
                cognome= args["cognome"],
                dataNascita = args["dataNascita"]
            )
            if(args["linkImmagine"]!=None): user.linkImmagine = args["linkImmagine"]


            db_session.add(user)
            db_session.commit()
        except OperationalError:
            return {
                        "msg": "error/s",
                        "cause": "invalid arguments",
                        "info": f'data format incorrect'
                    }
        except IntegrityError:
            return {
                        "msg": "error/s",
                        "cause": "invalid arguments",
                        "info": f'there is already someone using this email'
                    }
        
        return {
            "msg": "ok",
            "info": "registrazione avvenuta con successo"
        }


class SignUpVenditore(Resource):
    def post(self):
        args = venditoreArgs.parse_args()
        salt = bcrypt.gensalt()
        print(args)

        for key, value in args.items():
            if(value != None and len(value)<2):
                return {
                    "msg": "error/s",
                    "cause": "missing arguments",
                    "info": f'{key} has no value'
                }

        try:
            user = Utente(
                email=args["email"], 
                password=bcrypt.hashpw(args["password"].encode("utf8"), salt),
                nome= args["nome"],
                cognome= args["cognome"],
                dataNascita = args["dataNascita"]
            )
            if(args["linkImmagine"]!=None): user.linkImmagine = args["linkImmagine"]
            
            db_session.add(user)
            db_session.commit()
            print(user.id)
            vend = Venditore(
                idUtente=user.id,
                nomeAzienda=args["nomeAzienda"],
                partitaIva=args["partitaIva"],
                indirizzo=args["indirizzo"],
                provincia=args["provincia"],
                cap=args["cap"]
            )

            db_session.add(vend)
            db_session.commit()
        except OperationalError:
            return {
                        "msg": "error/s",
                        "cause": "invalid arguments",
                        "info": f'data format incorrect'
                    }
        except IntegrityError:
            return {
                        "msg": "error/s",
                        "cause": "invalid arguments",
                        "info": f'there is already someone using this email'
                    }
        
        return {
            "msg": "ok",
            "info": "registrazione avvenuta con successo"
        }


class Login(Resource):
    def post(self):
        args = loginArgs.parse_args()
        user = db_session.query(Utente).filter(Utente.email == args["email"]).first()

        if user== None:
            return {
                        "msg": "error/s",
                        "cause": "problem with password or username",
                        "info": f'hai sbagliato username o password'
                    }

        #print(user.password) #worka
        if  not bcrypt.checkpw(args["password"].encode("utf8"), user.password.encode("utf8")):
            return {
                        "msg": "error/s",
                        "cause": "problem with password or username",
                        "info": f'hai sbagliato username o password'
                    }

        
        print();
        vend = None
        if(user.venditore!=None):
            vend = user.venditore.serialize()

        token = jwt.encode({
            "user": user.serialize(),
            "vend": vend
        }, os.environ.get("JWT_SECRET"), algorithm="HS256");
        
        return {
            "token": token
        }


api.add_resource(ProdottiRoute, '/prodotti')
api.add_resource(SignUp, '/signUp')
api.add_resource(SignUpVenditore, '/signUpVenditore')
api.add_resource(Login, '/login')




if __name__ == "__main__":
    app.run(debug=True)