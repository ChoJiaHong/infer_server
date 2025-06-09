from .event_bus import event_bus


def setup_default_monitors(queue):
    """Initialize default monitors and start them."""
    from .rps_monitor import RPSMonitor
    from .queue_monitor import QueueSizeMonitor

    # Instantiate monitors (they subscribe themselves to the event bus)
    RPSMonitor()
    QueueSizeMonitor(queue)

    event_bus.start_all()

__all__ = ["event_bus", "setup_default_monitors"]
