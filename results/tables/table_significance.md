**Paired comparisons on ndcg@5 (randomisation test, Holm-corrected)**

| system          | vs       |   mean_diff |   diff_ci_low |   diff_ci_high |   cohens_dz |   wins |   ties |   losses |   p_randomization |   p_randomization_holm |
|:----------------|:---------|------------:|--------------:|---------------:|------------:|-------:|-------:|---------:|------------------:|-----------------------:|
| improved        | baseline |      -0.007 |        -0.186 |          0.175 |      -0.031 |      2 |      1 |        2 |             1.000 |                  1.000 |
| improved_no_cf  | improved |      -0.009 |        -0.192 |          0.165 |      -0.042 |      1 |      3 |        1 |             1.000 |                  1.000 |
| improved_no_qu  | improved |      -0.368 |        -0.704 |         -0.064 |      -0.883 |      0 |      2 |        3 |             0.250 |                  1.000 |
| improved_no_syn | improved |       0.000 |         0.000 |          0.000 |     nan     |      0 |      5 |        0 |             1.000 |                  1.000 |
| improved_oracle | improved |      -0.199 |        -0.406 |         -0.022 |      -0.816 |      0 |      2 |        3 |             0.248 |                  1.000 |
