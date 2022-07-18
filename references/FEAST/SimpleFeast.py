from feast.feast import (
    CMIM,
    discCMIM,
    BetaGamma,
    discBetaGamma,
    CondMI,
    discCondMI,
    DISR,
    discDISR,
    ICAP,
    discICAP,
    JMI,
    discJMI,
    MIM,
    discMIM,
    mRMR_D,
    disc_mRMR_D,
    weightedCMIM,
    discWeightedCMIM,
    weightedCondMI,
    discWeightedCondMI,
    weightedDISR,
    discWeightedDISR,
    weightedJMI,
    discWeightedJMI,
    weightedMIM,
    discWeightedMIM
)
import pandas as pd
import numpy as np
from sklearn.datasets import load_boston
from sklearn.preprocessing import MinMaxScaler
from logging import getLogger, DEBUG


log = getLogger()
log.setLevel(DEBUG)


boston = load_boston()
data_set = pd.DataFrame(data=boston.data, columns=boston.feature_names).to_numpy()
labels = pd.DataFrame(data=boston.target, columns=['Labels']).to_numpy()

x, y = data_set.shape
# set all weights equally
weights = [1.0 / x] * x

RUN_NORMAL = True
RUN_DISC = False

print("Feature Names")
print(boston.feature_names)
print("=============================================")

def print_results(func, fn_cols, original):
    feature_names = original.columns.tolist()
    selected_features = [feature_names[idx] for idx in fn_cols]
    print(f"{str(func)} picked {selected_features}")

if RUN_NORMAL:
    selected_features, feature_scores = BetaGamma(data_set, labels, 2, 1.0, 1.0)
    print_results(BetaGamma, selected_features, pd.DataFrame(data=boston.data, columns=boston.feature_names))

    funcs = [CondMI, DISR, ICAP, JMI, MIM, mRMR_D]
    for func in funcs:
        selected_features, feature_scores = func(data_set, labels, 2)
        print_results(func, selected_features, pd.DataFrame(data=boston.data, columns=boston.feature_names))

    funcs = [weightedCMIM, weightedCondMI, weightedDISR, weightedJMI, weightedMIM]
    for func in funcs:
        selected_features, feature_scores = func(data_set, labels, weights, 2)
        print_results(func, selected_features, pd.DataFrame(data=boston.data, columns=boston.feature_names))


if RUN_DISC:

    selected_features, feature_scores = discBetaGamma(data_set, labels, 2, 1.0, 1.0)
    print_results(discBetaGamma, selected_features, pd.DataFrame(data=boston.data, columns=boston.feature_names))

    # CMIM is actually a discrete function even though it has its own disc function. We need to use discretized data
    funcs = [CMIM]
    for func in funcs:
        selected_features, feature_scores = func(data_set, labels, 2)
        print_results(func, selected_features, pd.DataFrame(data=boston.data, columns=boston.feature_names))
    
    funcs = [discCMIM, discCondMI, discDISR, discICAP, discJMI, discMIM, discmRMR_D]
    for func in funcs:
        selected_features, feature_scores = func(data_set, labels, 2)
        print_results(func, selected_features, pd.DataFrame(data=boston.data, columns=boston.feature_names))

    funcs = [discWeightedCMIM, discWeightedCondMI, discWeightedDISR, discWeightedJMI, discWeightedMIM]
    for func in funcs:
        selected_features, feature_scores = func(data_set, labels, weights, 2)
        print_results(func, selected_features, pd.DataFrame(data=boston.data, columns=boston.feature_names))

