from dotenv import load_dotenv

load_dotenv()

from chatbot import Chatbot


def main():
    bot = Chatbot()
    print("Chatbot RAG iniciado. Digite 'sair' para encerrar.")
    while True:
        pergunta = input("\nVocê: ")
        if pergunta.lower() == "sair":
            break
        resposta = bot.perguntar(pergunta)
        print(f"Bot: {resposta}")


if __name__ == "__main__":
    main()
