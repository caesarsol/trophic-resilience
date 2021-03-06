import os

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import networkx as nx

from rr_model.network import Network
from rr_model.model import Industry

from utils.resilience_metrics import resilience
from utils.plotting import plot_trophic, plot_sim
from utils.sim import simulate_wage_shock

sns.set(rc={'figure.figsize': (12, 8)})
np.random.seed(11148705)

def generate_network(firms: int,
        theta_two = None,
        d = None, 
        theta_one = 0.2,
        overhead = 0.,
        params = {"lambda": 0.3, "beta": 0.95}
    ) -> Network:

    theta_two = theta_two or np.random.uniform(0.2, 0.3, firms)

    inds = [
        Industry(
            fixed_overhead=overhead,
            alpha=3,
            theta_one=theta_one,
            theta_two=t,
            params=params,
            ind_id=n
        ) for n, t in enumerate(theta_two)
    ]

    d = d or np.tril(np.random.uniform(0, 1, size=(firms, firms)), -1)

    return Network(inds, d)


def main_two(
    iters = 30, rec_th = .99,
    cache = False, verbose = True, cached_res_path = "simulations/result.csv"
):

    if cache and os.path.isfile(cached_res_path):
        if verbose:
            print("Using cached file!")

        df = pd.read_csv(cached_res_path)

        return df

    res = []

    for j in range(iters):

        net = generate_network(6)

        troph = net.trophic_inc

        if verbose: print(f"  {j+1}/{iters} -> incoherence:", troph, end='\r')

        df = simulate_wage_shock(net, f=2, verbose=False)

        df.columns = [f"Industry {i}" for i in df.columns]

        s, t = resilience(
            df,
            rec_th=rec_th
        )

        datum = {
            "shock": s.mean().tolist(),
            "incoherence": troph,
            "time to recovery":t.mean().tolist()
        }

        res.append(datum)

    res = pd.DataFrame(res)

    res.to_csv(cached_res_path, index=False)

    fig, axes = plot_trophic(res)

    fig.savefig("plots/coherence_corr.png")

    return res

def main_one(n = 5, f = 2, len_shock = 20):
    net = generate_network(n)

    sim = simulate_wage_shock(net, f=2, verbose=True, len_shock=len_shock)

    sim.to_csv("sim.csv")

    fig, ax = plot_sim(sim)

    pl = "s" if n > 1 else ""
    ax.set_title(f"A {f - 1:.0%} wage shock with {n} firm{pl}")
    
    ax.axvline(len_shock, linestyle="--", c="r")

    fig.savefig("plots/wage_shock.png")
    

if __name__ == '__main__':

    main_one(n=5, f=2)
