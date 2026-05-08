def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    if "evader" in self_role:
        mode = "evade"
    elif "pursuer" in self_role:
        mode = "pursue"
    else:
        scores = observation.get("scores")
        my_s = op_s = 0.0
        if isinstance(scores, dict):
            my_s = scores.get("self", scores.get("me", scores.get("agent", 0.0))) or 0.0
            op_s = scores.get("opponent", scores.get("opp", scores.get("enemy", 0.0))) or 0.0
        mode = "evade" if float(my_s) >= float(op_s) else "pursue"

    moves = []
    order = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    def mhd(x, y):
        return abs(x - ox) + abs(y - oy)

    best = None
    best_val = None
    for dx, dy, nx, ny in moves:
        if mode == "pursue" and nx == ox and ny == oy:
            return [dx, dy]
        d = mhd(nx, ny)
        # tie-breaker uses preference to keep moving along the main axis toward/away
        axis = (abs(nx - sx) != 0) + (abs(ny - sy) != 0)
        val = -d if mode == "evade" else d
        # add small deterministic bias: prefer reducing/increasing x distance first then y
        bx = abs(nx - ox) - abs(sx - ox)
        by = abs(ny - oy) - abs(sy - oy)
        val += (0.01 * (-bx if mode == "evade" else bx) + 0.001 * (-by if mode == "evade" else by)) + 0.0001 * axis
        if best is None or (val > best_val if mode == "evade" else val < best_val):
            best = (dx, dy)
            best_val = val

    return [int(best[0]), int(best[1])]