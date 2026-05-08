def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p[:2]) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p[:2]) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)
    self_terr = set(tuple(p[:2]) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set(tuple(p[:2]) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    resources = [tuple(p[:2]) for p in (observation.get("resources") or []) if p and len(p) >= 2]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if (sx, sy) in obstacles:
        moves = [(0, 0)]

    neigh = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    adj_unclaimed_from_terr = []
    for (x, y) in self_terr:
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if (nx, ny) in unclaimed and inb(nx, ny):
                adj_unclaimed_from_terr.append((nx, ny))
    adj_unclaimed_from_terr = adj_unclaimed_from_terr if adj_unclaimed_from_terr else list(unclaimed)

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        score = 0
        if (nx, ny) in self_terr:
            score += 0.2
        if (nx, ny) in unclaimed:
            score += 4.0
        if (nx, ny) in opp_terr:
            score += 6.0
        if (nx, ny) in opp_terr or (nx, ny) in unclaimed:
            score += 1.0 / (1 + abs(nx - ox) + abs(ny - oy))

        if adj_unclaimed_from_terr:
            dmin = min(abs(nx - tx) + abs(ny - ty) for (tx, ty) in adj_unclaimed_from_terr)
            score += 2.5 / (1 + dmin)

        if resources:
            rx, ry = min(resources, key=lambda r: abs(nx - r[0]) + abs(ny - r[1]))
            dr = abs(nx - rx) + abs(ny - ry)
            score += 0.5 / (1 + dr)

        # Minor tie-breaker: prefer moving away from opponent if tie
        score += 0.01 * (abs(nx - ox) + abs(ny - oy))

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return list(best) if best is not None else [0, 0]