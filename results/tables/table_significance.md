**Paired comparisons on ndcg@5 (randomisation test, Holm-corrected)**

| system          | vs       |   mean_diff |   diff_ci_low |   diff_ci_high |   cohens_dz |   wins |   ties |   losses |   p_randomization |   p_randomization_holm |
|:----------------|:---------|------------:|--------------:|---------------:|------------:|-------:|-------:|---------:|------------------:|-----------------------:|
| improved        | baseline |       0.008 |        -0.092 |          0.093 |       0.067 |      2 |      2 |        1 |             1.000 |                  1.000 |
| improved_no_cf  | improved |      -0.025 |        -0.074 |          0.000 |      -0.447 |      0 |      4 |        1 |             1.000 |                  1.000 |
| improved_no_qu  | improved |      -0.058 |        -0.124 |          0.000 |      -0.718 |      0 |      3 |        2 |             0.499 |                  1.000 |
| improved_no_syn | improved |       0.000 |         0.000 |          0.000 |     nan     |      0 |      5 |        0 |             1.000 |                  1.000 |
| improved_oracle | improved |      -0.025 |        -0.074 |          0.000 |      -0.447 |      0 |      4 |        1 |             1.000 |                  1.000 |
