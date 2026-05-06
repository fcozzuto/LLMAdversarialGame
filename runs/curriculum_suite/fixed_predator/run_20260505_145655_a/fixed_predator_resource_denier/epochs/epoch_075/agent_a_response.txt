def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Denier-style: prioritize resources where we can match/beat the opponent soon.
    best = None
    for dx, dy, nx, ny in moves:
        score = -10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Strongly contest resources opponent is closer to; also slightly favor nearer targets.
            s = (od - sd) * 28 - sd
            # If we are far behind, penalize more.
            if sd > od:
                s -= (sd - od) * 10
            # Tiny tie-breaker for deterministic preference.
            s -= (rx * 0.001 + ry * 0.001)
            if s > score:
                score = s
        # Prefer not to waste moves when scores are close: slight bias toward staying closer to selected high-value cells.
        score -= (man(nx, ny, sx, sy) * 0.001)
        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]