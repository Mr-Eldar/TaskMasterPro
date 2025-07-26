from aiogram.fsm.state import State, StatesGroup


class AddNewCategory(StatesGroup):
    name = State()


class AddNewCategoryPlan(StatesGroup):
    category = State()
    name = State()
    description = State()
    photo = State()


class DeleteWorkTasks(StatesGroup):
    category = State()
    hisUnderstand = State()


class DeleteTaskItem(StatesGroup):
    category = State()
    plan = State()
    hisUnderstand = State()


class EditWorkTask(StatesGroup):
    category = State()
    new_name = State()
    hisUnderstand = State()


class EditTaskItem(StatesGroup):
    category = State()
    plan = State()
    new_info = State()
    hisUnderstand = State()
    final = State()


class BackNow(StatesGroup):
    backNow = State()