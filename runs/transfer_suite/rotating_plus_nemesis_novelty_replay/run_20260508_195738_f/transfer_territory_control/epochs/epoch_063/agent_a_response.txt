def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def neighbors8(px, py):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = px + dx, py + dy
                    if inb(nx, ny):
                        yield nx, ny

    # Frontier targets: unclaimed cells adjacent to opponent territory, else any unclaimed
    frontier = set()
    if opp:
        for ox, oy in opp:
            for nx, ny in neighbors8(ox, oy):
                if (nx, ny) in unclaimed:
                    frontier.add((nx, ny))
    targets = list(frontier) if frontier else list(unclaimed)
    if not targets:
        return [0, 0]
    # Choose nearest target deterministically
    targets.sort(key=lambda t: (abs(t[0] - x) + abs(t[1] - y), t[0], t[1]))
    tx, ty = targets[0]

    best = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        val = 0
        # Immediate territory effects
        if (nx, ny) in opp:
            val += 6
        elif (nx, ny) in unclaimed:
            val += 3
        # Prefer moving toward target
        dist = abs(nx - tx) + abs(ny - ty)
        val += 5 - dist * 1.2
        # Prefer stepping into cells that are adjacent to opponent territory (creates counterclaim pressure)
        adj_opp = 0
        for ax, ay in neighbors8(nx, ny):
            if (ax, ay) in opp:
                adj_opp += 1
        val += adj_opp * 0.6
        # Avoid letting opponent immediately approach unclaimed cells: move that increases distance from target is penalized
        val -= (abs(x - tx) + abs(y - ty) - dist) < 0
        cand = (val, dx, dy, nx, ny)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]