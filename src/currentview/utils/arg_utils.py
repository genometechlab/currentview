from dataclasses import fields, is_dataclass


def _split_and_normalize_configs(
    model_config, preprocess_config, kwargs, *, logger, ModelConfig, PreprocessConfig
):
    """Return (final_gmm_cfg, final_pp_cfg) after resolving dicts/objects/**kwargs."""
    # 1) Field name sets
    model_fields = {f.name for f in fields(ModelConfig)}
    pp_fields = {f.name for f in fields(PreprocessConfig)}

    # 2) Start with empty dicts
    model_dict: dict = {}
    pp_dict: dict = {}

    # 3) If caller passed dicts, take them
    if isinstance(model_config, dict):
        model_dict.update(model_config)
        model_config = None  # canonicalize to object later
    if isinstance(preprocess_config, dict):
        pp_dict.update(preprocess_config)
        preprocess_config = None

    # 4) Split mixed kwargs into per-config piles
    unknown = []
    for k, v in (kwargs or {}).items():
        if k in model_fields and k in pp_fields:
            # Extremely unlikely; if it happens, be explicit
            logger.warning(
                f"Ambiguous kwarg '{k}' appears in both configs; assigning to {ModelConfig.__name__} by default."
            )
            model_dict.setdefault(k, v)
        elif k in model_fields:
            model_dict.setdefault(k, v)
        elif k in pp_fields:
            pp_dict.setdefault(k, v)
        else:
            unknown.append(k)

    if unknown:
        raise TypeError(f"Unknown config kwargs: {unknown}")

    # 5) Build objects, applying precedence
    # Precedence within each config: object > dict > kwargs (but kwargs already merged in dict)
    # If explicit object was provided, we respect its values and ignore same-named overrides.
    if model_config is None:
        model_config = ModelConfig(**model_dict)
    else:
        # object provided: keep it as-is; ignore any overlapping dict entries
        pass

    if preprocess_config is None:
        preprocess_config = PreprocessConfig(**pp_dict)
    else:
        # object provided: keep it as-is; ignore any overlapping dict entries
        pass

    return model_config, preprocess_config
