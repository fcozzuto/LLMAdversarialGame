def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    opp_terr = observation.get("opponent_territory", []) or []
    unclaimed = observation.get("unclaimed_cells", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    opp_set = set(tuple(p) for p in opp_terr)
    un_set = set(tuple(p) for p in unclaimed)
    self_set = set(tuple(p) for p in (observation.get("self_territory", []) or []))

    # Prefer: capture opponent territory if possible; else expand to unclaimed near our boundary;
    # keep some distance from opponent to reduce immediate counter-capture.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in opp_set:
            base = 12.0
        elif (nx, ny) in un_set:
            base = 6.0
        elif (nx, ny) in self_set:
            base = 2.0
        else:
            base = 1.0

        # Estimate opportunity: adjacent cells count (unclaimed + opponent territory).
        adj = 0
        for adx, ady in dirs:
            ax, ay = nx + adx, ny + ady
            if not inb(ax, ay) or (ax, ay) in obstacles:
                continue
            if (ax, ay) in un_set:
                adj += 1
            if (ax, ay) in opp_set:
                adj += 2

        # Safety: don't give the opponent an easy next capture.
        dist = md(nx, ny, ox, oy)
        safety = 0.35 * dist

        score = base + 0.6 * adj + safety

        # Tiny deterministic tie-breaker: prefer moves that reduce distance to target-ish direction (toward opponent if invading, else away).
        if (nx, ny) in opp_set:
            steer = -0.02 * dist
        else:
            steer = 0.02 * dist
        score += steer

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]