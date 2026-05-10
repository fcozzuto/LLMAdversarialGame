def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = list(observation.get("unclaimed_cells") or [])
    resources = list(observation.get("resources") or [])

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    targets = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            targets.append((x, y))
    if not targets:
        targets = [tuple(p) for p in unclaimed[:60]]  # keep it small

    if not targets:
        # simple deterministic fallback: move away from opponent if possible
        best = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles or (nx, ny) in opp_t:
                continue
            d = abs(nx - ox) + abs(ny - oy)
            if d > best[0] or (d == best[0] and (dx, dy) < (best[1], best[2])):
                best = (d, dx, dy)
        dx, dy = best[1], best[2]
        if best[0] == 10**9:
            return [0, 0]
        return [dx, dy]

    opp_pen = abs(sx - ox) + abs(sy - oy)
    bestv = -10**18
    bestm = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles or (nx, ny) in opp_t:
            continue
        mind = 10**9
        for tx, ty in targets:
            if (tx, ty) in obstacles:
                continue
            d = abs(tx - nx) + abs(ty - ny)
            if d < mind:
                mind = d
        # Prefer reaching targets, avoid being too close to opponent, prefer unclaimed.
        un = 1 if (nx, ny) in set(unclaimed) else 0
        od = abs(nx - ox) + abs(ny - oy)
        v = (-mind) * 10 + un * 3 + od - opp_pen * 0.01
        if v > bestv or (v == bestv and (dx, dy) < bestm):
            bestv = v
            bestm = (dx, dy)

    return [bestm[0], bestm[1]]