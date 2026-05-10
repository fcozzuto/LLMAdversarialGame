def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or [0, 0])
    ox, oy = map(int, observation.get("opponent_position") or [0, 0])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    un_set = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []) if x is not None and y is not None)
    their_set = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []) if x is not None and y is not None)
    our_set = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []) if x is not None and y is not None)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    neigh8 = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    best = None
    best_val = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        val = 0.0
        if (nx, ny) in un_set:
            val += 2.4
        if (nx, ny) in their_set:
            val += 3.2
        if (nx, ny) in our_set:
            val += 0.6

        adj_un = 0
        for ddx, ddy in neigh8:
            ax, ay = nx + ddx, ny + ddy
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in un_set:
                adj_un += 1
        val += 0.35 * adj_un

        # Deterministic tie-break: prioritize closer to opponent while keeping high val.
        dist_opp = abs(nx - ox) + abs(ny - oy)
        if val > best_val or (val == best_val and (best is None or dist_opp < best[0] or (dist_opp == best[0] and (dx, dy) < best[1]))):
            best_val = val
            best = (dist_opp, (dx, dy))

    return [int(best[1][0]), int(best[1][1])]