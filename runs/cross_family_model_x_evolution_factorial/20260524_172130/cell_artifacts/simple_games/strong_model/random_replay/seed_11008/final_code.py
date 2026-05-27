def choose_move(observation):
    def clamp_step(v):
        if v > 0:
            return 1
        if v < 0:
            return -1
        return 0

    def step_towards(src, dst):
        return [clamp_step(dst[0] - src[0]), clamp_step(dst[1] - src[1])]

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def safe_pos(v, default=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            try:
                return (int(v[0]), int(v[1]))
            except Exception:
                return default
        return default

    obs = observation if isinstance(observation, dict) else {}
    env = obs.get("environment_name", "resource_collection")

    self_pos = safe_pos(obs.get("self_position"))
    opp_pos = safe_pos(obs.get("opponent_position"), self_pos)

    gw = obs.get("grid_width", 0)
    gh = obs.get("grid_height", 0)
    try:
        gw = int(gw)
    except Exception:
        gw = 0
    try:
        gh = int(gh)
    except Exception:
        gh = 0

    if gw > 0 and gh > 0:
        center = (gw // 2, gh // 2)
    else:
        center = self_pos

    if env == "pursuit_evasion":
        role = obs.get("self_role", "pursuer")
        if role == "pursuer":
            return step_towards(self_pos, opp_pos)

        corners = [(0, 0), (0, max(0, gh - 1)), (max(0, gw - 1), 0), (max(0, gw - 1), max(0, gh - 1))]
        if corners:
            target = max(corners, key=lambda c: manhattan(c, opp_pos))
            return step_towards(self_pos, target)
        return step_towards(self_pos, center)

    if env == "territory_control":
        targets = obs.get("unclaimed_cells") or obs.get("opponent_territory") or obs.get("neutral_cells") or []
        best = None
        best_score = None
        for item in targets:
            p = safe_pos(item, None)
            if p is None:
                continue
            score = manhattan(self_pos, p)
            if best is None or score < best_score:
                best = p
                best_score = score
        if best is not None:
            return step_towards(self_pos, best)
        return step_towards(self_pos, center)

    resources = obs.get("resources") or obs.get("resource_positions") or []
    best = None
    best_score = None
    for item in resources:
        p = safe_pos(item, None)
        if p is None:
            continue
        score = manhattan(self_pos, p)
        if best is None or score < best_score:
            best = p
            best_score = score
    if best is not None:
        return step_towards(self_pos, best)

    dx = clamp_step(self_pos[0] - opp_pos[0])
    dy = clamp_step(self_pos[1] - opp_pos[1])
    if dx == 0 and dy == 0:
        return step_towards(self_pos, center)
    return [dx, dy]
