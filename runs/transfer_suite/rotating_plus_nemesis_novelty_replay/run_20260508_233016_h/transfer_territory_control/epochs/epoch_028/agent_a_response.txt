def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    ox, oy = observation["opponent_position"]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Try to "poke" opponent territory if possible; otherwise expand to nearest unclaimed.
    nearest_unclaimed = None
    if unclaimed:
        nearest_unclaimed = min(unclaimed, key=lambda c: dist((sx, sy), c))
    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny, dx, dy = sx, sy, 0, 0
        cell = (nx, ny)

        sc = 0.0
        if cell in self_terr:
            sc += 0.2
        if cell in unclaimed:
            sc += 1.2
        if cell in opp_terr:
            sc += 3.0  # flipping on entry is valuable

        # Prefer moving closer to target (unclaimed) and also closer to opponent when we can flip.
        d_opp = dist(cell, (ox, oy))
        sc += -0.03 * d_opp

        if nearest_unclaimed is not None:
            sc += -0.08 * dist(cell, nearest_unclaimed)
        else:
            sc += -0.01 * d_opp

        # If we are adjacent to opponent territory, favor stepping into it even without being directly on it yet.
        # (This helps avoid stalling on boundaries.)
        adj_opp = False
        for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            ax, ay = nx + adx, ny + ady
            if inb(ax, ay) and (ax, ay) in opp_terr:
                adj_opp = True
                break
        if adj_opp:
            sc += 0.6
            if cell not in opp_terr:
                sc += 0.15 * (1.0 if (abs(nx - ox) <= 2 and abs(ny - oy) <= 2) else 0.0)

        # Deterministic tie-break: smallest dx, then smallest dy magnitude via tuple ordering
        if sc > best_score or (sc == best_score and (dx, dy) < (best[0], best[1]) if best else True):
            best_score = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]