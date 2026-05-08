def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    if "evader" in self_role:
        mode = "evade"
    elif "pursuer" in self_role:
        mode = "pursue"
    else:
        scores = observation.get("scores") or {}
        my_s = 0.0
        op_s = 0.0
        if isinstance(scores, dict):
            my_s = scores.get("self", scores.get("me", scores.get("agent", 0.0))) or 0.0
            op_s = scores.get("opponent", scores.get("opp", scores.get("enemy", 0.0))) or 0.0
        mode = "evade" if float(my_s) >= float(op_s) else "pursue"

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def best_corner(from_x, from_y):
        bc = corners[0]
        best = -1
        for cx, cy in corners:
            d = (cx - from_x) * (cx - from_x) + (cy - from_y) * (cy - from_y)
            if d > best:
                best = d
                bc = (cx, cy)
        return bc

    tx, ty = best_corner(ox, oy) if mode == "evade" else best_corner(sx, sy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        step_bias = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)

        if mode == "pursue":
            # Prefer smaller distance; if tied, cut off by moving toward the corner farthest from us.
            val = (d2, -step_bias)
        else:
            # Prefer larger distance; if tied, run toward the corner farthest from the pursuer.
            val = (-d2, step_bias)

        if best is None or val < best:
            best = val
            best_move = [dx, dy]

    return best_move