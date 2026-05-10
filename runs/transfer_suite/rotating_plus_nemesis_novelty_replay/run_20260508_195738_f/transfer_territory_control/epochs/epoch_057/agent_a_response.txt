def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def adj_count(nx, ny):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ax, ay = nx + dx, ny + dy
                if inb(ax, ay) and (ax, ay) not in obs:
                    if (ax, ay) in unclaimed or (ax, ay) in selft or (ax, ay) in opp:
                        c += 1
        return c

    def opp_touch(nx, ny):
        t = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ax, ay = nx + dx, ny + dy
                if inb(ax, ay) and (ax, ay) in opp:
                    t += 1
        return t

    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        if (nx, ny) in unclaimed:
            base = 5.5
        elif (nx, ny) in selft:
            base = 2.2
        elif (nx, ny) in opp:
            base = 4.8
        else:
            base = 1.0

        dist_center = abs(nx - cx) + abs(ny - cy)
        score = base
        score += 0.35 * adj_count(nx, ny)
        score -= 0.08 * dist_center
        score += 0.2 * opp_touch(nx, ny)

        if score > best_score or (score == best_score and [dx, dy] != best_move and (dx, dy) < tuple(best_move)):
            best_score = score
            best_move = [dx, dy]

    return best_move