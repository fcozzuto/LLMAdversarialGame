def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h

    if opp:
        cx = sum(px for px, py in opp) / float(len(opp))
        cy = sum(py for px, py in opp) / float(len(opp))
    else:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def manh(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def neighbor_opponent(nx, ny):
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                if (nx + ddx, ny + ddy) in opp:
                    return True
        return False

    def neighbor_unclaimed(nx, ny):
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                if (nx + ddx, ny + ddy) in unclaimed:
                    return True
        return False

    # Move ordering preference to break ties deterministically
    order = sorted(dirs, key=lambda d: (abs(d[0]) + abs(d[1]), d[0], d[1]))

    best = -10**18
    best_move = [0, 0]
    for dx, dy in order:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Base: approach opponent center to meet their claim
        score = -0.9 * (abs(nx - cx) + abs(ny - cy))

        # Territory/entry effects: flipping on entry enabled
        if (nx, ny) in opp:
            score += 12.0
        elif (nx, ny) in unclaimed:
            score += 5.5
        elif (nx, ny) in selft:
            score += 1.5
        else:
            score += 0.5

        # Frontier bonuses: go where it increases the chance to flip next turn
        if neighbor_opponent(nx, ny):
            score += 3.5
        if neighbor_unclaimed(nx, ny):
            score += 2.0

        # Mild penalty for drifting away from own current area early
        score += -0.1 * (min((abs(nx - sx) + abs(ny - sy)) for sx, sy in selft) if selft else 0)

        # Strongly avoid pointless oscillation with no progress: prefer staying only if best is low
        if dx == 0 and dy == 0:
            score -= 1.0

        if score > best:
            best = score
            best_move = [dx, dy]

    return best_move