def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))

    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = min(corners, key=lambda c: abs(c[0] - x) + abs(c[1] - y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def adj_opp(nx, ny):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (nx + dx, ny + dy) in opp:
                    return 1
        return 0

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        if (nx, ny) in selft:
            base = 1.0
        elif (nx, ny) in unclaimed:
            base = 3.0
        elif (nx, ny) in opp:
            base = 2.5
        else:
            base = 0.5

        dist_corner = abs(nx - tx) + abs(ny - ty)
        dist_opp = abs(nx - ox) + abs(ny - oy)

        score = base
        score += -1.8 * dist_corner
        score += -0.25 * dist_opp
        score += 0.9 * adj_opp(nx, ny)

        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]