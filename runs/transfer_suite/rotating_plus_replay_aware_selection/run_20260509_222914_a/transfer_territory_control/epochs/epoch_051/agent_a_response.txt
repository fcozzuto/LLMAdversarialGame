def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cellset(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    self_t = cellset("self_territory")
    opp_t = cellset("opponent_territory")
    unclaimed = cellset("unclaimed_cells")
    op = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(op[0]), int(op[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**9

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) in opp_t:
            base = 10
        elif (nx, ny) in unclaimed:
            base = 7
        elif (nx, ny) in self_t:
            base = 4
        else:
            base = 1

        # Prefer pushing away from opponent to reduce counter-claim exposure
        dist = man(nx, ny, ox, oy)
        score = base + (0.02 * dist) - (0.01 * man(sx, sy, ox, oy))

        # Light tie-break toward closer-to-center for stable expansion
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score += -0.001 * (abs(nx - cx) + abs(ny - cy))

        # Deterministic ordering tie-breaker via move index
        idx = moves.index((dx, dy))
        score += -1e-6 * idx

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]