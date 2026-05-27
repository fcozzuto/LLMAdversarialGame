def choose_move(observation):
    def clamp_step(v):
        return -1 if v < 0 else (1 if v > 0 else 0)

    def pos(v, default=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return v[0], v[1]
        return default

    def move_toward(src, dst):
        sx, sy = src
        tx, ty = dst
        return [clamp_step(tx - sx), clamp_step(ty - sy)]

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_target(src, items, prefer_max=False):
        if not items:
            return None
        best = None
        best_score = None
        for it in items:
            if not isinstance(it, (list, tuple)) or len(it) < 2:
                continue
            p = (it[0], it[1])
            score = manhattan(src, p)
            if best is None or (prefer_max and score > best_score) or (not prefer_max and score < best_score):
                best = p
                best_score = score
        return best

    env = observation.get("environment_name", "resource_collection")
    sx, sy = pos(observation.get("self_position"))
    ox, oy = pos(observation.get("opponent_position"), (sx, sy))
    gw = observation.get("grid_width", 0) or 0
    gh = observation.get("grid_height", 0) or 0

    if env == "pursuit_evasion":
        role = observation.get("self_role", "pursuer")
        if role == "pursuer":
            return move_toward((sx, sy), (ox, oy))
        corners = [(0, 0), (0, max(0, gh - 1)), (max(0, gw - 1), 0), (max(0, gw - 1), max(0, gh - 1))]
        target = best_target((ox, oy), corners, prefer_max=True)
        if target is None:
            return [0, 0]
        return move_toward((sx, sy), target)

    if env == "territory_control":
        targets = observation.get("unclaimed_cells") or observation.get("opponent_territory") or observation.get("territory_targets") or []
        target = best_target((sx, sy), targets, prefer_max=False)
        if target is not None:
            return move_toward((sx, sy), target)
        opp = observation.get("opponent_position")
        if isinstance(opp, (list, tuple)) and len(opp) >= 2:
            return move_toward((sx, sy), (opp[0], opp[1]))
        return [0, 0]

    resources = observation.get("resources") or observation.get("resource_positions") or []
    target = best_target((sx, sy), resources, prefer_max=False)
    if target is not None:
        return move_toward((sx, sy), target)

    # Defensive fallback: drift toward opponent if visible, otherwise stay still.
    if isinstance(observation.get("opponent_position"), (list, tuple)):
        return move_toward((sx, sy), (ox, oy))
    return [0, 0]
