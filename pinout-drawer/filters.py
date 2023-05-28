def create_filter_func(filter_cfg):
    if isinstance(filter_cfg, dict):
        cond = list(filter_cfg.keys())[0]
        parts = [create_filter_func(x) for x in list(filter_cfg.values())[0]]
        if cond == "and":
            return lambda signals: all(part(signals) for part in parts)
        elif cond == "or":
            return lambda signals: any(part(signals) for part in parts)
        else:
            print(f"invalid cond {cond}")
    else:
        return lambda signals: filter_cfg in signals


def create_filter_func_array(filters_cfg):
    filters_fns = []
    for filter_cfg in filters_cfg:
        fn = create_filter_func(filter_cfg)
        filters_fns.append(fn)

    return lambda signals: any(part(signals) for part in filters_fns)
