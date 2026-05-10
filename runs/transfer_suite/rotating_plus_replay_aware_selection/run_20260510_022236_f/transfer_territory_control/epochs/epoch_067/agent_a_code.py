def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    lead = int(observation.get("self_territory_count") or 0) >= int(observation.get("opponent_territory_count") or 0)
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))
    if unclaimed:
        unclaimed = [c for c in unclaimed if isinstance(c, (list, tuple)) and len(c) >= 2]
    unclaimed.sort(key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy), c[1], c[0]))

    opp = (ox, oy)
    target = unclaimed[0] if (lead and unclaimed) else opp

    def score(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        d = abs(nx - target[0]) + abs(ny - target[1])
        if lead and unclaimed:
            bonus = (0 if (nx, ny) != target else 50)
        else:
            bonus = 0
        dist_opp = abs(nx - ox) + abs(ny - oy)
        rel = dist_opp if lead else -dist_opp
        return -d * 10 + bonus + rel

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score(nx, ny)
        if sc > best_score or (sc == best_score and (dx, dy) < best):
            best_score = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]