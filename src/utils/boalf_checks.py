def validate_boalf(boa, bmu_map=None, event_series=None):
    """
    Validate BOALF dataset for local constraint modelling.

    Parameters
    ----------
    boa : pd.DataFrame
        Raw BOALF data
    bmu_map : pd.DataFrame (optional)
        BMU metadata with region/fuel info
    event_series : pd.Series (optional)
        Binary constraint_event aligned to settlement periods

    Returns
    -------
    dict
        Summary diagnostics
    """

    import pandas as pd

    results = {}

    print("\n=========================")
    print("BOALF VALIDATION CHECK")
    print("=========================\n")

    # -------------------------
    # 1. Basic structure
    # -------------------------
    print("1. Dataset size")
    print("-------------------------")
    print(f"Rows: {len(boa):,}")
    print(f"Unique BMUs: {boa['bmUnit'].nunique()}")
    print()

    # -------------------------
    # 2. Fuel type check
    # -------------------------
    if 'fuelType' in boa.columns:
        print("2. Fuel types")
        print("-------------------------")
        fuel_counts = boa['fuelType'].value_counts()
        print(fuel_counts.head(10))
        print()

        battery_flag = fuel_counts.index.str.contains('BAT', case=False).any()
        if battery_flag:
            print("⚠️ WARNING: Battery units detected — filter required")
        else:
            print("✔ No obvious battery units detected")
        print()

    # -------------------------
    # 3. Volume sanity
    # -------------------------
    if 'acceptedVolume' in boa.columns:
        print("3. Accepted volume distribution")
        print("-------------------------")
        print(boa['acceptedVolume'].describe())
        print()

    # -------------------------
    # 4. Region check
    # -------------------------
    if bmu_map is not None:
        print("4. Region coverage")
        print("-------------------------")

        merged = boa.merge(bmu_map, on='bmUnit', how='left')

        if 'gsp_group' in merged.columns:
            region_counts = merged['gsp_group'].value_counts()
            print(region_counts.head(10))
            print()

            results['region_counts'] = region_counts

            if region_counts.nunique() > 5:
                print("⚠️ Wide regional spread — not SW-specific")
            else:
                print("✔ Likely regionally filtered")
        else:
            print("No 'gsp_group' column found in mapping")

        print()

    else:
        print("4. Region check skipped (no bmu_map provided)\n")

    # -------------------------
    # 5. Event frequency
    # -------------------------
    if event_series is not None:
        print("5. Event frequency")
        print("-------------------------")

        rate = event_series.mean()
        print(f"Constraint event rate: {rate:.3f}")

        if rate > 0.3:
            print("⚠️ Very high event rate — likely not true constraints")
        elif rate < 0.01:
            print("⚠️ Very low event rate — may be too strict")
        else:
            print("✔ Reasonable event frequency")

        print()

        # -------------------------
        # 6. Persistence check
        # -------------------------
        print("6. Persistence check")
        print("-------------------------")

        lag = event_series.shift(1)

        persistence = pd.crosstab(
            lag, event_series, normalize='index'
        )

        print(persistence)
        print()

        if 1 in persistence.index:
            stay_prob = persistence.loc[1, 1]
            print(f"P(event continues | event): {stay_prob:.2f}")

            if stay_prob > 0.6:
                print("✔ Strong persistence (expected)")
            else:
                print("⚠️ Weak persistence — may not be real constraints")

        print()

    else:
        print("5–6. Event checks skipped (no event_series provided)\n")

    print("=========================\n")

    return results