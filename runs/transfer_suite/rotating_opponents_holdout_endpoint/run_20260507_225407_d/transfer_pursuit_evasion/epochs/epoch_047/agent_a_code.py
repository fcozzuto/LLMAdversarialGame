def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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
        if isinstance(scores, dict):
            my_s = scores.get("self", scores.get("me", scores.get("agent", 0.0))) or 0.0
            op_s = scores.get("opponent", scores.get("opp", scores.get("enemy", 0.0))) or 0.0
        else:
            my_s, op_s = 0.0, 0.0
        mode = "evade" if float(my_s) >= float(op_s) else "pursue"

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def dist(x, y):
        return abs(x - ox) + abs(y - oy)

    best = None
    best_score = None
    for dx, dy, nx, ny in moves:
        d = dist(nx, ny)
        if mode == "pursue":
            # prefer reducing manhattan, with secondary preference for smaller max(|dx|,|dy|)
            score = (-d, -max(abs(nx - ox), abs(ny - oy)))
        else:
            # prefer increasing distance, then prefer corners/edges to make zigzags harder
            corner = (nx in (0, w - 1)) and (ny in (0, h - 1))
            edge = (nx in (0, w - 1)) or (ny in (0, h - 1))
            score = (d, 1.0 if corner else 0.3 if edge else 0.0)
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best:
                best = (dx, dy)

    return [int(best[0]), int(best[1])]