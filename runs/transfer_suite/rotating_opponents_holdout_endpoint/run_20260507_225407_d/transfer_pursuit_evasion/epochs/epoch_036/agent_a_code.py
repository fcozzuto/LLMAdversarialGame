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

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    if "evader" in self_role and "pursuer" in opp_role:
        my_role = "evader"
    elif "pursuer" in self_role and "evader" in opp_role:
        my_role = "pursuer"
    else:
        scores = observation.get("scores", None)
        my_s, op_s = 0.0, 0.0
        if isinstance(scores, dict):
            my_s = scores.get("self", scores.get("me", scores.get("agent", 0.0))) or 0.0
            op_s = scores.get("opponent", scores.get("opp", scores.get("enemy", 0.0))) or 0.0
        role = "pursuer" if my_s <= op_s else "evader"
        my_role = role

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Simple deterministic obstacle "danger": prefer cells with fewer blocked neighbors
    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # danger: count blocked neighbors (higher is worse)
        danger = 0
        for ddx, ddy in neigh:
            tx, ty = nx + ddx, ny + ddy
            if not valid(tx, ty):
                danger += 1
        if my_role == "evader":
            dist = manh(nx, ny, ox, oy)
            # also avoid getting linearly "stepped on": penalize moves that reduce distance the most
            score = dist * 10 - danger * 0.5
        else:
            dist = manh(nx, ny, ox, oy)
            # try to move toward opponent, and mildly prefer moves that align with approach
            dir_align = (1 if (nx - sx) * (ox - sx) >= 0 else -1) + (1 if (ny - sy) * (oy - sy) >= 0 else -1)
            score = -dist * 10 + dir_align * 0.2 - danger * 0.2
        if best is None or (score > best_score) or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]