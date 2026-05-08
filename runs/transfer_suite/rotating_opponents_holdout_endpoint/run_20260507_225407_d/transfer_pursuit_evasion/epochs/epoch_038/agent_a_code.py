def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    opp_role = str(observation.get("opponent_role") or "").lower()
    if ("evader" in self_role and "pursuer" in opp_role) or (str(observation.get("self_role") or "").lower() == "evader"):
        role = "evader"
    elif ("pursuer" in self_role and "evader" in opp_role) or (str(observation.get("self_role") or "").lower() == "pursuer"):
        role = "pursuer"
    else:
        scores = observation.get("scores") or {}
        my_s = 0.0
        op_s = 0.0
        if isinstance(scores, dict):
            my_s = scores.get("self", scores.get("me", scores.get("agent", 0.0))) or 0.0
            op_s = scores.get("opponent", scores.get("opp", scores.get("enemy", 0.0))) or 0.0
        role = "pursuer" if float(my_s) <= float(op_s) else "evader"

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        val = -d if role == "pursuer" else d
        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [best[0], best[1]]