def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except:
            pass

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_pursuer = ("purs" in sr) and ("evad" not in sr)
    if not ("purs" in sr or "evad" in sr) and "purs" in orr:
        self_is_pursuer = False
    if ("evad" in sr) and ("purs" not in sr):
        self_is_pursuer = False
    if ("purs" in sr) and ("evad" in sr):
        self_is_pursuer = True

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        d = abs(x1 - x2) + abs(y1 - y2)
        return d

    def safe(x, y):
        return in_bounds(x, y) and (x, y) not in obs

    def mobility(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if safe(nx, ny):
                c += 1
        return c

    best = None
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        d = dist(nx, ny, ox, oy)
        mob = mobility(nx, ny)

        # Additional wall-avoidance: penalize being adjacent to obstacles too often
        adj = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                xx, yy = nx + ex, ny + ey
                if (xx, yy) in obs:
                    adj += 1

        # If roles: pursue reduces distance; evade increases distance.
        if self_is_pursuer:
            score = (-6 * d) + (0.6 * mob) - (2.0 * adj)
            # Prefer moves that more directly "aim" at opponent
            score += -0.15 * max(0, (abs(nx - ox) - abs(sx - ox)) + (abs(ny - oy) - abs(sy - oy)))
        else:
            score = (7.5 * d) + (0.9 * mob) - (2.2 * adj)
            # Prefer breaking immediate pursuit alignment (increase both coordinate differences)
            score += 0.12 * (abs(nx - ox) + abs(ny - oy) - (abs(sx - ox) + abs(sy - oy)))

        # Deterministic tie-break: favor staying still if equal score, else lexicographic on (dx,dy)
        if score > best_score:
            best_score = score
            best = (dx, dy)
        elif score == best_score and best is not None:
            if (dx, dy) == (0, 0) and best != (0, 0):
                best = (dx, dy)
            elif (dx, dy) == best:
                pass
            else:
                # lexicographic tie-break for determinism
                if (dx, dy) < best:
                    best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]