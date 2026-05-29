import time
from src.incidents.correlation import correlate_open_events
from src.config.settings import settings

def main():
    print(
        f"Correlation worker running every "
        f"{settings.auto_correlation_interval_seconds} seconds"
    )

    while True:
        try:
            created = correlate_open_events()
            if created:
                print("Created incidents:", created)
        except Exception as exc:
            print("Correlation error:", exc)

        time.sleep(settings.auto_correlation_interval_seconds)

if __name__ == "__main__":
    main()
