def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    # Deterministic tie-breaker: prefer earlier dirs in order
    best_score = None
    best_move = [0, 0]

    txs = (observation.get("turn_index", 0) or 0)

    for i, (dx, dy) in enumerate(dirs):
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        score = 0.0

        if (nx, ny) in selft:
            score += 2.5
        if (nx, ny) in unclaimed:
            score += 3.5
        if (nx, ny) in opp:
            # Flipping enabled on entry: take fights only if not too risky positionally
            score += 4.0

        # Prefer pushing toward edges (opponent likely center-claimer)
        dist_center = abs(nx - cx) + abs(ny - cy)
        score += dist_center * 0.15

        # Avoid getting trapped next to obstacles: penalize moves with many blocked neighbors
        blocked = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ax, ay = nx + ddx, ny + ddy
                if not inb(ax, ay) or (ax, ay) in obs:
                    blocked += 1
        score -= blocked * 0.05

        # Minor pressure to advance away from center over staying
        if dx == 0 and dy == 0:
            score -= 0.1

        # Deterministic tie-breaking
        if best_score is None or score > best_score + 1e-12 or (abs(score - best_score) <= 1e-12 and i < dirs.index(tuple(best_move))):
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]