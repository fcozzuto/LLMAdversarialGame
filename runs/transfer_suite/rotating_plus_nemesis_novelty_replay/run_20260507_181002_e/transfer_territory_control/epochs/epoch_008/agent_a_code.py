def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))

    if not unclaimed:
        unclaimed = set(resources)

    adj8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prefer expanding, but opportunistically flip if adjacent to opponent territory.
    # Deterministic tie-break order is dirs order.
    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        gain = 0.0
        if (nx, ny) in selfT:
            gain += 0.1
        elif (nx, ny) in oppT:
            gain += 2.2
        elif (nx, ny) in unclaimed:
            gain += 1.4
        else:
            gain += 0.0

        # Encourage territory growth toward unclaimed/resources; discourage getting too close only if no gain.
        d_to_opp = man((nx, ny), (ox, oy))
        proximity_penalty = 0.0 if gain > 0.0 else (3.0 / (1.0 + d_to_opp))

        # Mild edge preference for controlling boundaries.
        edge_bonus = 0.25 if (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1) else 0.0

        # If opponent nearby, slightly prefer moving into/near opponent territory (counterclaim).
        opp_adj = 0
        if oppT:
            for ax, ay in adj8:
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in oppT:
                    opp_adj = 1
                    break
        counter_bonus = 0.35 if opp_adj else 0.0

        score = gain + edge_bonus + counter_bonus - proximity_penalty + (0.02 * d_to_opp)

        if score > best_score + 1e-12:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]