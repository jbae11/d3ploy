import random
import sys
import os
import pytest
import d3ploy.solver as solver
import numpy as np
import d3ploy.NO_solvers as no

import statsmodels.api as sm
from arch import arch_model

ts = {}
for i in range(11):
    ts[i] = i
ts_list = list(ts.values())

def test_ma():
    # backstep is 5 by default
    answer = np.mean(ts_list[-5:])
    assert(no.predict_ma(ts) == answer)

def test_arma():
    model_fit = sm.tsa.ARMA(ts_list[-5:], (1, 0)).fit(disp=-1)
    forecast, std_err, conf_int = model_fit.forecast(5)
    answer = forecast[-1]
    # or just
    # answer = 8.73044396885388
    assert pytest.approx(no.predict_arma(ts), 1e-3) == answer

def test_arch():
    answer = 9.5
    assert pytest.approx(no.predict_arch(ts), 1e-3) == answer