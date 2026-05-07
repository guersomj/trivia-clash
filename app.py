import random
import streamlit as st
from questions import QUESTIONS

st.set_page_config(
    page_title="Trivia Clash",
    page_icon="🧠",
    layout="centered"
)

# -------------------------
# Inicializar memoria de la app
# -------------------------
if "game_started" not in st.session_state:
    st.session_state.game_started = False

if "game_finished" not in st.session_state:
    st.session_state.game_finished = False

if "players" not in st.session_state:
    st.session_state.players = []

if "scores" not in st.session_state:
    st.session_state.scores = {}

if "turn" not in st.session_state:
    st.session_state.turn = 0

if "question_count" not in st.session_state:
    st.session_state.question_count = 0

if "total_questions" not in st.session_state:
    st.session_state.total_questions = 10

if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "mode" not in st.session_state:
    st.session_state.mode = "Duelo de Categorías"
if "chain_position" not in st.session_state:
    st.session_state.chain_position = 0

if "chain_values" not in st.session_state:
    st.session_state.chain_values = [100, 200, 400, 800, 1500, 3000]

def get_random_question():
    if st.session_state.mode == "No era tan fácil":
        trick_questions = [q for q in QUESTIONS if q["type"] == "trick"]
        return random.choice(trick_questions)

    return random.choice(QUESTIONS)


def reset_game():
    st.session_state.game_started = False
    st.session_state.game_finished = False
    st.session_state.players = []
    st.session_state.scores = {}
    st.session_state.turn = 0
    st.session_state.question_count = 0
    st.session_state.current_question = None
    st.session_state.used_questions = []
    st.session_state.chain_position = 0


# -------------------------
# Pantalla principal
# -------------------------
st.title("🧠 Trivia Clash")
st.caption("Banco, duelo y trampas culturales.")

if not st.session_state.game_started and not st.session_state.game_finished:
    st.subheader("Configurar partida")

    player1 = st.text_input("Jugador 1", value="Alo")
    player2 = st.text_input("Jugador 2", value="Guersom")

    mode = st.selectbox(
        "Modo de juego",
        [
            "Duelo de Categorías",
            "Banco o Quiebra",
            "No era tan fácil"
        ]
    )

    total_questions = st.slider("Número de preguntas", 5, 30, 10)

    if st.button("Empezar partida"):
        st.session_state.players = [player1, player2]
        st.session_state.scores = {
            player1: 0,
            player2: 0
        }
        st.session_state.mode = mode
        st.session_state.total_questions = total_questions
        st.session_state.current_question = get_random_question()
        st.session_state.game_started = True
        st.rerun()


# -------------------------
# Juego activo
# -------------------------
elif st.session_state.game_started:
    current_player = st.session_state.players[st.session_state.turn]
    q = st.session_state.current_question

    st.subheader(f"Turno de: {current_player}")
    st.caption(f"Modo: {st.session_state.mode}")
    st.caption(f"Categoría: {q['category']} | Dificultad: {q['difficulty']}")

    progress = st.session_state.question_count / st.session_state.total_questions
    st.progress(progress)
if st.session_state.mode == "Banco o Quiebra":
    if st.session_state.chain_position == 0:
        current_chain_value = 0
    else:
        current_chain_value = st.session_state.chain_values[
            st.session_state.chain_position - 1
        ]

    st.info(f"Cadena actual: {current_chain_value} puntos")

    if st.button("Banco"):
        if current_chain_value > 0:
            st.session_state.scores[current_player] += current_chain_value
            st.session_state.chain_position = 0
            st.rerun()
        else:
            st.warning("No hay puntos para bancar todavía.")
    st.write(f"### {q['question']}")

    selected_answer = st.radio(
        "Elige tu respuesta:",
        q["options"],
        key=st.session_state.question_count
    )

    if st.button("Responder"):
    if selected_answer == q["answer"]:
        if st.session_state.mode == "Banco o Quiebra":
            max_position = len(st.session_state.chain_values)
            if st.session_state.chain_position < max_position:
                st.session_state.chain_position += 1
        else:
            st.session_state.scores[current_player] += 100
    else:
        if st.session_state.mode == "Banco o Quiebra":
            st.session_state.chain_position = 0

        st.session_state.question_count += 1

        if st.session_state.question_count >= st.session_state.total_questions:
            st.session_state.game_started = False
            st.session_state.game_finished = True
        else:
            st.session_state.turn = 1 - st.session_state.turn
            st.session_state.current_question = get_random_question()

        st.rerun()

    st.divider()

    st.write("## Marcador")
    for player, score in st.session_state.scores.items():
        st.write(f"**{player}:** {score} puntos")


# -------------------------
# Resultado final
# -------------------------
elif st.session_state.game_finished:
    st.subheader("Resultado final")

    scores = st.session_state.scores
    highest_score = max(scores.values())
    lowest_score = min(scores.values())

    winners = [
        player for player, score in scores.items()
        if score == highest_score
    ]

    losers = [
        player for player, score in scores.items()
        if score == lowest_score
    ]

    st.write("## Marcador final")

    for player, score in scores.items():
        st.write(f"**{player}:** {score} puntos")

    if len(winners) > 1:
        st.info("🤝 Empate. Nadie ganó, nadie perdió. Todos culturalmente sospechosos.")
    else:
        winner = winners[0]
        loser = losers[0]

        st.success(f"🏆 Ganador/a: {winner}")
        st.warning(f"El rival más débil fue: {loser}. Adiós.")

    if st.button("Jugar otra vez"):
        reset_game()
        st.rerun()
