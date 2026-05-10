def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    def toset(v):
        s = set()
        for p in v or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obst = toset(observation.get("obstacles"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))  # unused but included for completeness

    op = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(op[0]), int(op[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inside(x, y): return 0 <= x < w and 0 <= y < h

    # Prefer controlling space while denying opponent reach; avoid obstacles hard.
    def cell_score(x, y):
        if (x, y) in obst:
            return -10**8
        score = 0
        if (x, y) in oppT: score += 90
        elif (x, y) in unclaimed: score += 35
        elif (x, y) in selfT: score += 6
        else: score += 14  # edge/neutral
        # Centrality bias (territory_edge_claim tends to hug edges; we counter by taking safer center-ish tiles)
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dcent = abs(x - cx) + abs(y - cy)
        score += int(18 - dcent * 1.2)
        # Deny opponent: if this cell is closer to us than to them, it's valuable.
        du = abs(x - sx) + abs(y - sy)
        do = abs(x - ox) + abs(y - oy)
        score += int((do - du) * 3.5)
        # Gentle obstacle/edge avoidance
        score += int((x not in (0, w-1)) and (y not in (0, h-1)))
        return score

    # Candidate evaluation: look at immediate move and choose best next cell.
    best = (-10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        sc = cell_score(nx, ny)

        # If moving into/near unclaimed, prefer progressing along the "front" away from opponent.
        # Deterministic tie-breaker based on target cell.
        if (nx, ny) in unclaimed:
            sc += 12
        if abs(nx - ox) + abs(ny - oy) <= 1:
            sc -= 8  # avoid getting boxed in

        if sc > best[0] or (sc == best[0] and (nx, ny) < (best[1], best[2])):
            best = (sc, nx, ny)

    return [best[1] - sx, best[2] - sy]