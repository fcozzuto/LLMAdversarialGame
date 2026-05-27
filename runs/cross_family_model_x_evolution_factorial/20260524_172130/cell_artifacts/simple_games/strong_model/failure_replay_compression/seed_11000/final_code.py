def choose_move(observation):
    def clamp_step(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def as_pos(v, default=(0, 0)):
        if isinstance(v, dict):
            if "x" in v and "y" in v:
                return v.get("x", default[0]), v.get("y", default[1])
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return v[0], v[1]
        return default

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def step_toward(src, dst):
        return [clamp_step(dst[0] - src[0]), clamp_step(dst[1] - src[1])]

    def step_away(src, dst):
        return [clamp_step(src[0] - dst[0]), clamp_step(src[1] - dst[1])]

    def pick_best(items, score_fn, default=None):
        best_item = default
        best_score = None
        for item in items:
            score = score_fn(item)
            if best_score is None or score < best_score:
                best_score = score
                best_item = item
        return best_item

    env = observation.get("environment_name", "resource_collection")
    self_pos = as_pos(observation.get("self_position"), (0, 0))
    opp_pos = as_pos(observation.get("opponent_position"), self_pos)
    gw = observation.get("grid_width", 0) or 0
    gh = observation.get("grid_height", 0) or 0

    if env == "pursuit_evasion":
        role = observation.get("self_role", "pursuer")
        if role == "pursuer":
            return step_toward(self_pos, opp_pos)
        corners = []
        if gw and gh:
            corners = [(0, 0), (0, gh - 1), (gw - 1, 0), (gw - 1, gh - 1)]
        else:
            sx, sy = self_pos
            corners = [(sx - 1, sy - 1), (sx - 1, sy + 1), (sx + 1, sy - 1), (sx + 1, sy + 1)]
        target = pick_best(corners, lambda p: -manhattan(p, opp_pos), corners[0])
        return step_away(self_pos, opp_pos) if target is None else step_toward(self_pos, target)

    if env == "territory_control":
        targets = (
            observation.get("unclaimed_cells")
            or observation.get("opponent_territory")
            or observation.get("frontier")
            or []
        )
        parsed = [as_pos(t, self_pos) for t in targets]
        if parsed:
            # Prefer nearby expansion, but break ties by moving away from opponent pressure.
            def score(p):
                return manhattan(self_pos, p) * 3 - manhattan(opp_pos, p)
            best = pick_best(parsed, score, parsed[0])
            return step_toward(self_pos, best)
        if gw and gh:
            center = (gw // 2, gh // 2)
            return step_toward(self_pos, center)
        return [0, 0]

    resources = (
        observation.get("resources")
        or observation.get("resource_positions")
        or observation.get("resource_tiles")
        or []
    )
    parsed = [as_pos(r, self_pos) for r in resources]
    if parsed:
        # Prefer resources that are close to us and not too close to the opponent.
        def score(p):
            return manhattan(self_pos, p) * 2 - manhattan(opp_pos, p)
        best = pick_best(parsed, score, parsed[0])
        return step_toward(self_pos, best)

    if gw and gh:
        return step_toward(self_pos, (gw // 2, gh // 2))
    return step_toward(self_pos, opp_pos)
