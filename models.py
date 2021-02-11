from sqlalchemy import *
from sqlalchemy.ext.declarative import *
from sqlalchemy.orm import *
import os


engine = create_engine(os.getenv("DB"))

metadata = MetaData(bind=engine)

# mappa i metadati sulla connessione
db_session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()

Base.query = db_session.query_property()

class Utente(Base):
    __tablename__ = "utenti"
    __table_args__ = (
        UniqueConstraint('email'),
    )
    id = Column(Integer, primary_key=True)
    email = Column(String(200), nullable=False)
    password = Column(String(200), nullable=False)
    nome = Column(String(200), nullable=False)
    cognome = Column(String(200), nullable=False)
    dataNascita = Column(Date, nullable=False)
    linkImmagine = Column(String(200))
    venditore = relationship("Venditore", uselist=False, back_populates="utente")

    def serialize(self):
        return {"idUtente": self.id, "email":self.email, 
        "nome":
            self.nome, "cognome": self.cognome, 
            "dataNascita": self.dataNascita.strftime('%m/%d/%Y'), "linkImmagine": self.linkImmagine}

class Venditore(Base):
    __tablename__ = "venditori"
    __table_args__ = (
        UniqueConstraint('partitaIva'),
    )
    id = Column(Integer, primary_key=True)
    idUtente = Column(Integer, ForeignKey('utenti.id'))
    utente = relationship("Utente", back_populates="venditore")
    nomeAzienda = Column(String(200), nullable=False)
    partitaIva = Column(String(200), nullable=False)
    indirizzo = Column(String(200), nullable=False)
    provincia = Column(String(2), nullable=False)
    cap = Column(String(6), nullable=False)
    prodotti = relationship("Prodotto", backref="venditori", order_by="Prodotto.id")

    def serialize(self):
        return {
            "idVenditore": self.id,
            "nomeAzienda": self.nomeAzienda,
            "partitaIva": self.partitaIva,
            "indirizzo": self.indirizzo,
            "provincia": self.provincia,
            "cap": self.cap
        }

class Categoria(Base):
    __tablename__ = "categorie"
    __table_args__ = (
        UniqueConstraint('nome'),
    )
    id = Column(Integer, primary_key=True)
    nome = Column(String(200), nullable=False)
    colore = Column(String(10), nullable=False)
    prodotti = relationship("Prodotto", backref="categorie", order_by="Prodotto.id")

class Prodotto(Base):
    __tablename__ = "prodotti"
    id = Column(Integer, primary_key=True)
    idVenditore = Column(ForeignKey("venditori.id"))
    idCategoria = Column(ForeignKey("categorie.id"))
    nome = Column(String(200), nullable=False)
    descrizione = Column(String(400), nullable=False)
    prezzo = Column(Numeric(10,2), nullable=False)
    linkImmagine = Column(String(200))
    valuta = Column(String(5), nullable=False)

    def serialize(self):
        return {
            "idProdotto": self.id,
            "nome": self.nome,
            "descrizione": self.descrizione,
            "prezzo": self.prezzo,
            "linkImmagine": self.linkImmagine,
            "valuta": self.valuta
        }


if __name__ == "__main__":
    print("creating tables")
    Base.metadata.drop_all(engine)
    #Base.metadata.clear()
    Base.metadata.create_all(engine)

