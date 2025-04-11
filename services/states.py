from aiogram.fsm.state import State, StatesGroup


class ReportStates(StatesGroup):
    # Состояния для работы с заявками
    set_text = State()
    choose_order_id = State()
    end_creation_report = State()
    set_departments = State()
    set_status = State()

    # Edit states
    get_report_id = State()
    set_edited_report_text = State()
    change_report_for_send = State()

    waiting_for_report_id = State()


class TicketStates(StatesGroup):
    # Состояния для работы с заявками
    set_ticket_text = State()
    end_creation_order = State()
    set_department = State()
    set_subdivisions = State()
    get_ticket_id = State()
    # set_status = State()
    # set_workers = State()

    # Edit states
    set_edited_order_text = State()
    change_order_for_send = State()

    waiting_for_order_id = State()
