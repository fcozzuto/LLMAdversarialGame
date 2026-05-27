def choose_move(observation):
    def sgn(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def pos(val, default=(0, 0)):
        if isinstance(val, (list, tuple)) and len(val) >= 2:
            return val[0], val[1]
        return default

    def nearest(src, items):
        best = None
        best_d = None
        for item in items or []:
            x, y = pos(item, None)
            if x is None:
                continue
            d = abs(x - src[0]) + abs(y - src[1])
            if best_d is None or d < best_d:
                best_d = d
                best = (x, y)
        return best

    def step_toward(src, dst):
        if dst is None:
            return [0, 0]
        return [sgn(dst[0] - src[0]), sgn(dst[1] - src[1])]

    def step_away(src, dst):
        if dst is None:
            return [0, 0]
        return [sgn(src[0] - dst[0]), sgn(src[1] - dst[1])]

    env = observation.get("environment_name", "resource_collection")
    sx, sy = pos(observation.get("self_position"))
    ox, oy = pos(observation.get("opponent_position"), (sx, sy))

    if env == "pursuit_evasion":
        role = observation.get("self_role", "pursuer")
        if role == "pursuer":
            return step_toward((sx, sy), (ox, oy))
        gw = observation.get("grid_width", 0) or 0
        gh = observation.get("grid_height", 0) or 0
        corners = [(0, 0), (0, max(0, gh - 1)), (max(0, gw - 1), 0), (max(0, gw - 1), max(0, gh - 1))]
        target = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        move = step_toward((sx, sy), target)
        if move == [0, 0]:
            move = step_away((sx, sy), (ox, oy))
        return move

    if env == "territory_control":
        targets = observation.get("unclaimed_cells") or observation.get("opponent_territory") or observation.get("targets") or []
        if not targets:
            gw = observation.get("grid_width", 0) or 0
            gh = observation.get("grid_height", 0) or 0
            if gw and gh:
                return step_toward((sx, sy), (gw // 2, gh // 2))
            return [0, 0]
        target = nearest((sx, sy), targets)
        return step_toward((sx, sy), target)

    resources = observation.get("resources") or observation.get("resource_positions") or observation.get("resource_cells") or []
    target = nearest((sx, sy), resources)
    if target is not None:
        return step_toward((sx, sy), target)

    if env == "resource_collection":
        return step_toward((sx, sy), (ox, oy))
    return [0, 0]
