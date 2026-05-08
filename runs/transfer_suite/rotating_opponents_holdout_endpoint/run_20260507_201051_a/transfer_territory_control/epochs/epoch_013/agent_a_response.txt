def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick deterministic "frontier" targets: unclaimed cells adjacent to opponent territory; else any unclaimed.
    adj_frontier = []
    for (x, y) in opp_t:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                adj_frontier.append((nx, ny))
    if adj_frontier:
        # Choose best frontier by (dist to self, prefer higher y then x deterministically)
        best = min(adj_frontier, key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy), -c[1], -c[0]))
    else:
        all_un = [c for c in unclaimed if inb(c[0], c[1]) and c not in obstacles]
        best = min(all_un, key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy), -c[1], -c[0])) if all_un else (sx, sy)

    # Evaluate candidate moves by a simple deterministic heuristic.
    def cell_gain(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        g = 0
        if (nx, ny) in unclaimed:
            g += 3
        if (nx, ny) in opp_t:
            g += 1  # flipping on entry
        if (nx, ny) in self_t:
            g -= 1  # avoid "wasting" on already-owned
        # Distance shaping to chosen target
        g -= 0.05 * (abs(nx - best[0]) + abs(ny - best[1]))
        # Mild repulsion from opponent to reduce being "swept" (territory_sweeper)
        if opp_t:
            # deterministic nearest opp influence using first-min scan
            nearest_d = min(abs(nx - ox) + abs(ny - oy) for (ox, oy) in opp_t)
            g += 0.02 * nearest_d
        return g

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = cell_gain(nx, ny)
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]