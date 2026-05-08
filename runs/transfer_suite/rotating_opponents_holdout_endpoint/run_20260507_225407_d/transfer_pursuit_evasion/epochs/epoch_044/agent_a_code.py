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
    best_corner = corners[0]
    best_corner_score = -1 if mode == "evade" else 10**18
    for cx, cy in corners:
        d = (cx - ox) * (cx - ox) + (cy - oy) * (cy - oy)
        if mode == "evade":
            if d > best_corner_score:
                best_corner_score = d
                best_corner = (cx, cy)
        else:
            if d < best_corner_score:
                best_corner_score = d
                best_corner = (cx, cy)

    def clamp(x, a, b):
        return a if x < a else (b if x > b else x)

    moves = [-1, 0, 1]
    best = None
    best_score = -10**18 if mode == "evade" else 10**18

    for dy in moves:
        for dx in moves:
            nx, ny = clamp(sx + dx, 0, w - 1), clamp(sy + dy, 0, h - 1)
            if (nx, ny) in obstacles:
                continue
            dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            if mode == "evade":
                corner_dx, corner_dy = best_corner[0] - nx, best_corner[1] - ny
                corner2 = corner_dx * corner_dx + corner_dy * corner_dy
                score = dist2 * 1000 - corner2
                better = score > best_score
            else:
                corner_dx, corner_dy = best_corner[0] - nx, best_corner[1] - ny
                corner2 = corner_dx * corner_dx + corner_dy * corner_dy
                score = -dist2 * 1000 - corner2
                better = score < best_score

            if best is None or better:
                best = (dx, dy)
                best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]