from app.metrics.ticket_count_executor import TicketCountExecutor
from app.metrics.ticket_list_executor import TicketListExecutor


METRIC_EXECUTORS = {
    "ticket_count": TicketCountExecutor,
    "ticket_list": TicketListExecutor,
}
