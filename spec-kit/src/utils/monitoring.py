"""
Monitoring and alerting utilities for the Unified Physical AI & Humanoid Robotics Learning Book project.
This module provides system monitoring, metrics collection, and alerting capabilities.
"""

import time
import psutil
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


@dataclass
class Metric:
    """Represents a single metric measurement."""
    name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str] = None


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Represents an alert."""
    name: str
    message: str
    severity: AlertSeverity
    timestamp: datetime
    details: Dict[str, Any] = None


class MetricsCollector:
    """Collects system and application metrics."""

    def __init__(self):
        self.metrics = []
        self.alerts = []
        self.logger = logging.getLogger(__name__)

    def collect_system_metrics(self) -> List[Metric]:
        """Collect system-level metrics."""
        metrics = []

        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        metrics.append(Metric("cpu_percent", cpu_percent, "%", datetime.now()))

        cpu_count = psutil.cpu_count()
        metrics.append(Metric("cpu_count", cpu_count, "count", datetime.now()))

        # Memory metrics
        memory = psutil.virtual_memory()
        metrics.append(Metric("memory_percent", memory.percent, "%", datetime.now()))
        metrics.append(Metric("memory_used", memory.used / (1024**3), "GB", datetime.now()))
        metrics.append(Metric("memory_available", memory.available / (1024**3), "GB", datetime.now()))
        metrics.append(Metric("memory_total", memory.total / (1024**3), "GB", datetime.now()))

        # Disk metrics
        disk = psutil.disk_usage('/')
        metrics.append(Metric("disk_percent", disk.percent, "%", datetime.now()))
        metrics.append(Metric("disk_used", disk.used / (1024**3), "GB", datetime.now()))
        metrics.append(Metric("disk_total", disk.total / (1024**3), "GB", datetime.now()))

        # Network metrics
        network = psutil.net_io_counters()
        metrics.append(Metric("network_bytes_sent", network.bytes_sent, "bytes", datetime.now()))
        metrics.append(Metric("network_bytes_recv", network.bytes_recv, "bytes", datetime.now()))

        self.metrics.extend(metrics)
        return metrics

    def collect_application_metrics(self) -> List[Metric]:
        """Collect application-specific metrics."""
        metrics = []

        # Add application-specific metrics here
        # For example, API response times, database connection counts, etc.
        metrics.append(Metric("active_connections", 10, "count", datetime.now()))
        metrics.append(Metric("requests_per_minute", 100, "count", datetime.now()))

        self.metrics.extend(metrics)
        return metrics

    def get_metrics_by_name(self, name: str) -> List[Metric]:
        """Get metrics by name."""
        return [m for m in self.metrics if m.name == name]

    def get_latest_metric_value(self, name: str) -> Optional[float]:
        """Get the latest value for a specific metric."""
        metrics = self.get_metrics_by_name(name)
        if metrics:
            return metrics[-1].value
        return None


class AlertManager:
    """Manages alerting based on metrics and thresholds."""

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.thresholds = {}
        self.alert_callbacks = []
        self.logger = logging.getLogger(__name__)

    def set_threshold(self, metric_name: str, threshold_value: float, severity: AlertSeverity, operator: str = ">"):
        """
        Set a threshold for a metric.

        Args:
            metric_name: Name of the metric
            threshold_value: Threshold value
            severity: Alert severity
            operator: Comparison operator ('>', '<', '>=', '<=', '==', '!=')
        """
        self.thresholds[metric_name] = {
            "value": threshold_value,
            "severity": severity,
            "operator": operator
        }

    def check_thresholds(self) -> List[Alert]:
        """Check all thresholds and generate alerts if needed."""
        alerts = []

        for metric_name, threshold_config in self.thresholds.items():
            latest_value = self.metrics_collector.get_latest_metric_value(metric_name)
            if latest_value is not None:
                threshold_value = threshold_config["value"]
                severity = threshold_config["severity"]
                operator = threshold_config["operator"]

                condition_met = False
                if operator == ">":
                    condition_met = latest_value > threshold_value
                elif operator == "<":
                    condition_met = latest_value < threshold_value
                elif operator == ">=":
                    condition_met = latest_value >= threshold_value
                elif operator == "<=":
                    condition_met = latest_value <= threshold_value
                elif operator == "==":
                    condition_met = latest_value == threshold_value
                elif operator == "!=":
                    condition_met = latest_value != threshold_value

                if condition_met:
                    alert = Alert(
                        name=f"Threshold Alert: {metric_name}",
                        message=f"Metric {metric_name} ({latest_value}) {operator} threshold {threshold_value}",
                        severity=severity,
                        timestamp=datetime.now(),
                        details={
                            "metric_name": metric_name,
                            "current_value": latest_value,
                            "threshold_value": threshold_value,
                            "operator": operator
                        }
                    )
                    alerts.append(alert)
                    self.metrics_collector.alerts.append(alert)
                    self.logger.warning(f"Alert generated: {alert.message}")

        return alerts

    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Add a callback function to be called when alerts are generated."""
        self.alert_callbacks.append(callback)

    def trigger_alert_callbacks(self, alert: Alert):
        """Trigger all alert callbacks."""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}")


class EmailNotifier:
    """Handles email notifications for alerts."""

    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, from_email: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.logger = logging.getLogger(__name__)

    def send_alert_email(self, alert: Alert, to_emails: List[str]):
        """Send an alert via email."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.name}"

            body = f"""
            Alert: {alert.name}
            Message: {alert.message}
            Severity: {alert.severity.value}
            Time: {alert.timestamp}

            Details: {json.dumps(alert.details, indent=2, default=str) if alert.details else 'N/A'}
            """

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.from_email, to_emails, text)
            server.quit()

            self.logger.info(f"Alert email sent to: {to_emails}")
        except Exception as e:
            self.logger.error(f"Failed to send alert email: {e}")


class MonitoringService:
    """Main monitoring service that coordinates metrics collection and alerting."""

    def __init__(self, email_notifier: Optional[EmailNotifier] = None):
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager(self.metrics_collector)
        self.email_notifier = email_notifier
        self.is_running = False
        self.logger = logging.getLogger(__name__)

        # Set up default thresholds
        self._setup_default_thresholds()

        # Set up alert callbacks
        self._setup_alert_callbacks()

    def _setup_default_thresholds(self):
        """Set up default thresholds for common metrics."""
        self.alert_manager.set_threshold("cpu_percent", 80, AlertSeverity.HIGH, ">")
        self.alert_manager.set_threshold("memory_percent", 85, AlertSeverity.HIGH, ">")
        self.alert_manager.set_threshold("disk_percent", 90, AlertSeverity.HIGH, ">")

    def _setup_alert_callbacks(self):
        """Set up default alert callbacks."""
        if self.email_notifier:
            def email_callback(alert: Alert):
                self.email_notifier.send_alert_email(alert, ["admin@example.com"])
            self.alert_manager.add_alert_callback(email_callback)

        def log_callback(alert: Alert):
            self.logger.warning(f"Alert: {alert.name} - {alert.message}")
        self.alert_manager.add_alert_callback(log_callback)

    async def collect_and_check(self):
        """Collect metrics and check thresholds."""
        # Collect system metrics
        self.metrics_collector.collect_system_metrics()

        # Collect application metrics
        self.metrics_collector.collect_application_metrics()

        # Check thresholds and generate alerts
        alerts = self.alert_manager.check_thresholds()

        return alerts

    async def run_monitoring_loop(self, interval: int = 60):
        """
        Run the monitoring loop continuously.

        Args:
            interval: Interval between metric collections in seconds
        """
        self.is_running = True
        self.logger.info("Starting monitoring loop...")

        while self.is_running:
            try:
                await self.collect_and_check()
                await asyncio.sleep(interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    def stop_monitoring(self):
        """Stop the monitoring loop."""
        self.is_running = False
        self.logger.info("Monitoring stopped")

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        cpu_percent = self.metrics_collector.get_latest_metric_value("cpu_percent")
        memory_percent = self.metrics_collector.get_latest_metric_value("memory_percent")
        disk_percent = self.metrics_collector.get_latest_metric_value("disk_percent")

        health_status = "healthy"
        if cpu_percent and cpu_percent > 90:
            health_status = "degraded"
        if memory_percent and memory_percent > 95:
            health_status = "degraded"
        if disk_percent and disk_percent > 95:
            health_status = "degraded"

        return {
            "status": health_status,
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent
            },
            "recent_alerts": [alert.__dict__ for alert in self.metrics_collector.alerts[-5:]]  # Last 5 alerts
        }

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of collected metrics."""
        return {
            "total_metrics": len(self.metrics_collector.metrics),
            "total_alerts": len(self.metrics_collector.alerts),
            "latest_collection": self.metrics_collector.metrics[-1].timestamp if self.metrics_collector.metrics else None,
            "metrics_by_type": {
                "system": len([m for m in self.metrics_collector.metrics if m.name.startswith(('cpu', 'memory', 'disk', 'network'))]),
                "application": len([m for m in self.metrics_collector.metrics if not m.name.startswith(('cpu', 'memory', 'disk', 'network'))])
            }
        }


# Global monitoring service instance
monitoring_service = None


def initialize_monitoring(
    smtp_server: str = None,
    smtp_port: int = 587,
    email_username: str = None,
    email_password: str = None,
    from_email: str = None
) -> MonitoringService:
    """
    Initialize the monitoring service.

    Args:
        smtp_server: SMTP server for email notifications
        smtp_port: SMTP port
        email_username: Email username
        email_password: Email password
        from_email: Sender email address

    Returns:
        Initialized monitoring service
    """
    global monitoring_service

    email_notifier = None
    if all([smtp_server, email_username, email_password, from_email]):
        email_notifier = EmailNotifier(
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            username=email_username,
            password=email_password,
            from_email=from_email
        )

    monitoring_service = MonitoringService(email_notifier=email_notifier)
    return monitoring_service


def get_monitoring_service() -> Optional[MonitoringService]:
    """Get the global monitoring service instance."""
    return monitoring_service


# Performance monitoring decorators
def monitor_performance(metric_name: str, unit: str = "seconds"):
    """
    Decorator to monitor function performance.

    Args:
        metric_name: Name for the performance metric
        unit: Unit of measurement
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if monitoring_service:
                    monitoring_service.metrics_collector.metrics.append(
                        Metric(metric_name, duration, unit, datetime.now())
                    )

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if monitoring_service:
                    monitoring_service.metrics_collector.metrics.append(
                        Metric(metric_name, duration, unit, datetime.now())
                    )

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def log_api_performance(endpoint: str):
    """
    Decorator to log API endpoint performance.

    Args:
        endpoint: API endpoint name
    """
    return monitor_performance(f"api_response_time_{endpoint.replace('/', '_')}", "seconds")


# Health check endpoints
async def health_check() -> Dict[str, Any]:
    """Perform a health check of the system."""
    if monitoring_service:
        return monitoring_service.get_system_health()
    else:
        return {
            "status": "unknown",
            "timestamp": datetime.now().isoformat(),
            "message": "Monitoring service not initialized"
        }


async def metrics_check() -> Dict[str, Any]:
    """Get metrics summary."""
    if monitoring_service:
        return monitoring_service.get_metrics_summary()
    else:
        return {
            "message": "Monitoring service not initialized"
        }


__all__ = [
    "Metric",
    "AlertSeverity",
    "Alert",
    "MetricsCollector",
    "AlertManager",
    "EmailNotifier",
    "MonitoringService",
    "monitoring_service",
    "initialize_monitoring",
    "get_monitoring_service",
    "monitor_performance",
    "log_api_performance",
    "health_check",
    "metrics_check"
]