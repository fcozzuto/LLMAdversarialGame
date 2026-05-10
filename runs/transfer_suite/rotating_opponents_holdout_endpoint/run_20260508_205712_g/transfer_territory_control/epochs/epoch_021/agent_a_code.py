def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    unclaimed = observation.get("unclaimed_cells", []) or []
    uc = set((int(x), int(y)) for x, y in unclaimed)

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory", []) or []))
    oppT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory", []) or []))

    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    best_score = -10**18

    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        # Prefer unclaimed cells; else prefer not to step into opponent territory; otherwise chase opponent.
        score = 0
        if (nx, ny) in uc:
            score += 1000
        if (nx, ny) in oppT:
            score -= 500
        # Encourage expanding territory/advancing toward opponent.
        score -= (abs(nx - ox) + abs(ny - oy))
        # Mild preference to keep within own territory if unclaimed not available.
        if selfT and (nx, ny) in selfT:
            score += 10
        # Deterministic tie-break: fixed ordering via index and score.
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best