from aiogram.fsm.state import State, StatesGroup

class InterviewState(StatesGroup):
    choosing_vacancy = State()
    waiting_for_answer = State()