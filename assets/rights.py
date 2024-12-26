RIGHTS = {
    2: {
        "role_name": "Диспетчер",
        "rights": {
            "create_order",
            "change_order_status",
            "send_order",
            "delete_order",
            "check_order_info",
        },
    },
    1: {
        "role_name": "Рабочий",
        "rights": {"change_order_status", "check_order_info"},
    },
}
RIGHTS_ASSERTIONS = {
    "create_order": "Создать заявку",
    "change_order_status": "Сменить статус заявки",
    "send_order": "Отправить заявку",
    "delete_order": "Удалить заявку",
    "check_order_info": "Посмотреть информацию по заявке",
}
