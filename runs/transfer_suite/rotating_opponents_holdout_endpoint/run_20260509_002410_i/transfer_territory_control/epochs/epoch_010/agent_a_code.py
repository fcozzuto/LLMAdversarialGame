def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []

    # Try to attack/expand onto cells adjacent to opponent territory (frontier grab).
    opp_frontier = set()
    if opp_t:
        for px, py in opp_t:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
                nx, ny = px + dx, py + dy
                if inside(nx, ny) and (nx, ny) not in obstacles and ((nx, ny) in unclaimed or (nx, ny) in self_t):
                    opp_frontier.add((nx, ny))
    if not opp_frontier:
        # Fallback: prioritize any unclaimed near center and near opponent.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        def key_uc(p):
            x, y = p
            return (abs(x - cx) + abs(y - cy), abs(x - ox) + abs(y - oy), y, x)
        opp_frontier = set(sorted(unclaimed, key=key_uc)[:8])

    # Evaluate one-step move.
    best = (0, 0)
    best_sc = -10**18
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        sc = 0
        if (nx, ny) in opp_t:
            sc += 25  # strong flip
        elif (nx, ny) in unclaimed:
            sc += 10
        elif (nx, ny) in self_t:
            sc += 3

        # Target pressure: move toward frontier cells or toward center-opponent region.
        d_front = min((abs(nx - tx) + abs(ny - ty) for tx, ty in opp_frontier), default=10**9)
        sc += 18 - min(d_front, 18)

        # Prefer threatening positions near opponent and center.
        sc += 5 - min(abs(nx - ox) + abs(ny - oy), 10)
        cx, cy = (w - 1) // 2, (h - 1) // 2
        sc += 2 - min(abs(nx - cx) + abs(ny - cy), 6) / 3.0

        # Small tie-break: deterministic ordering by destination then dx,dy.
        if sc > best_sc or (sc == best_sc and (ny, nx, dx, dy) < (best[1], best[0], 0, 0)):
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]