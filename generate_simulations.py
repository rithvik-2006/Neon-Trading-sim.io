# # generate_simulations.py
# import os
# import uuid
# import numpy as np
# import psycopg
# from dotenv import load_dotenv

# # ---------------- CONFIG ----------------
# SYMBOL = "NIFTY50"
# MINUTES = 390
# MU = 0.0
# SIGMA = 0.015
# MAX_SIMULATIONS = 200   # stop when reached
# BATCH_SIZE = 10            # simulations per run
# # ----------------------------------------

# load_dotenv()
# DATABASE_URL = os.getenv("DATABASE_URL")
# def simulate_intraday_prices(start_price, mu, sigma, minutes=390):
#     dt = 1 / minutes
#     prices = [start_price]

#     for _ in range(minutes - 1):
#         shock = np.random.normal()
#         price = prices[-1] * np.exp(
#             (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * shock
#         )
#         prices.append(price)

#     return prices
# def get_simulation_count(conn):
#     with conn.cursor() as cur:
#         cur.execute("SELECT COUNT(DISTINCT simulation_id) FROM simulations;")
#         return cur.fetchone()[0]
# def insert_simulation(conn, prices):
#     sim_id = uuid.uuid4()
#     rows = [
#         (sim_id, SYMBOL, minute, float(price))
#         for minute, price in enumerate(prices)
#     ]

#     with conn.cursor() as cur:
#         cur.executemany(
#             """
#             INSERT INTO simulations
#             (simulation_id, symbol, minute, price)
#             VALUES (%s, %s, %s, %s)
#             """,
#             rows
#         )
#     conn.commit()
# def main():
#     with psycopg.connect(DATABASE_URL) as conn:
#         current_count = get_simulation_count(conn)
#         print(f"Current simulations: {current_count}")

#         if current_count >= MAX_SIMULATIONS:
#             print("Simulation limit reached. Exiting.")
#             return

#         for _ in range(BATCH_SIZE):
#             prices = simulate_intraday_prices(
#                 start_price=14000,
#                 mu=MU,
#                 sigma=SIGMA,
#                 minutes=MINUTES
#             )
#             insert_simulation(conn, prices)
#             print("Inserted 1 simulation")

#         print("Batch completed.")
# if __name__ == "__main__":
#     main()

# generate_simulations.py
import os
import uuid
import numpy as np
import psycopg
from dotenv import load_dotenv

# ---------------- CONFIG ----------------
SYMBOL = "NIFTY50"
MINUTES = 390
MU = 0.00000222
SIGMA = 0.00050040
MAX_SIMULATIONS = 200
BATCH_SIZE = 10
# ----------------------------------------

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


def simulate_intraday_prices(start_price, mu, sigma, minutes=390):
    dt = 1 / minutes
    prices = [start_price]

    for _ in range(minutes - 1):
        shock = np.random.normal()
        price = prices[-1] * np.exp(
            (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * shock
        )
        prices.append(price)

    return prices


def get_simulation_count(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(DISTINCT simulation_id) FROM simulations;")
        return cur.fetchone()[0]


def insert_simulation(conn, prices):
    sim_id = uuid.uuid4()
    rows = [
        (sim_id, SYMBOL, minute, float(price))
        for minute, price in enumerate(prices)
    ]

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO simulations
            (simulation_id, symbol, minute, price)
            VALUES (%s, %s, %s, %s)
            """,
            rows
        )
    conn.commit()


def main():
    with psycopg.connect(DATABASE_URL) as conn:
        current_count = get_simulation_count(conn)
        print(f"Current simulations: {current_count}")

        if current_count >= MAX_SIMULATIONS:
            print("Simulation limit reached. Exiting.")
            return

        remaining = MAX_SIMULATIONS - current_count
        to_generate = min(BATCH_SIZE, remaining)

        for _ in range(to_generate):
            prices = simulate_intraday_prices(
                start_price=14000,
                mu=MU,
                sigma=SIGMA,
                minutes=MINUTES
            )
            insert_simulation(conn, prices)
            print("Inserted 1 simulation")

        print("Batch completed.")


if __name__ == "__main__":
    main()
