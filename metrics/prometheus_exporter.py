import logging
from prometheus_client import start_http_server, Gauge

class PrometheusExporter:
    def __init__(self, port: int = 8001):
        self.port = port
        self.queue_avg = Gauge('queue_size_avg', 'Average queue size over the last interval')
        self.queue_max = Gauge('queue_size_max', 'Maximum queue size over the last interval')
        self.queue_min = Gauge('queue_size_min', 'Minimum queue size over the last interval')
        self.queue_latest = Gauge('queue_size_latest', 'Latest queue size sample')
        self.queue_zero_ratio = Gauge('queue_zero_ratio', 'Percentage of zero-size queue samples')
        self.rps = Gauge('requests_per_second', 'Number of requests processed per second')
        self.completed_rps = Gauge('completed_requests_per_second', 'Number of requests completed per second')
        start_http_server(self.port)
        logging.getLogger(__name__).info('Prometheus exporter running on port %s', self.port)

    def update_queue(self, stats: dict):
        """Update queue related metrics with a stats dictionary."""
        if not stats:
            return
        self.queue_avg.set(stats.get('avg', 0))
        self.queue_max.set(stats.get('max', 0))
        self.queue_min.set(stats.get('min', 0))
        self.queue_latest.set(stats.get('latest', 0))
        self.queue_zero_ratio.set(stats.get('zero_ratio', 0))

    def update_rps(self, rps: float):
        """Update the RPS metric."""
        self.rps.set(rps)

    def update_completed_rps(self, rps: float):
        """Update the completed requests per second metric."""
        self.completed_rps.set(rps)
