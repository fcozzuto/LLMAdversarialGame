def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def step_ok(dx, dy):
        nx, ny = sx + dx, sy + dy
        return inb(nx, ny) and (nx, ny) not in obstacles

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # If we can immediately flip an adjacent opponent cell, do it.
    for dx, dy in candidates:
        if dx == 0 and dy == 0:
            continue
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in oppT and (nx, ny) not in obstacles:
            return [dx, dy]

    target = None
    if unclaimed:
        # Bias toward unclaimed near us, and slightly toward those closer to opponent (edge pressure).
        bestc, bestv = None, None
        for (x, y) in unclaimed:
            v = dist(x, y, sx, sy) * 2 + dist(x, y, ox, oy)
            if bestv is None or v < bestv or (v == bestv and (x, y) in oppT):
                bestv = v
                bestc = (x, y)
        target = bestc
    else:
        # Default: head toward opponent, but slightly bias toward center to keep expansion stable.
        cx, cy = w // 2, h // 2
        target = (ox * 0.7 + cx * 0.3, oy * 0.7 + cy * 0.3)

    best = (0, 0)
    bestscore = None
    tx, ty = target
    for dx, dy in candidates:
        if not step_ok(dx, dy):
            continue
        nx, ny = sx + dx, sy + dy
        # Encourage entering unclaimed; mildly discourage re-entering own territory.
        score = dist(nx, ny, sx, sy) * 0
        if (nx, ny) in oppT:
            score -= 40
        if (nx, ny) in selfT:
            score += 5
        # Main objective: reduce distance to target.
        score += dist(nx, ny, tx, ty)
        if bestscore is None or score < bestscore:
            bestscore = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]