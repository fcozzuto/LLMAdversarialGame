def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    if isinstance(unclaimed, dict):
        unclaimed = list(unclaimed.keys())
    unclaimed_set = set(tuple(p) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    aggressive = int(observation.get("self_territory_count", 0)) <= int(observation.get("opponent_territory_count", 0))

    best = (sx, sy)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        s = 0.0
        if (nx, ny) in unclaimed_set:
            s += 1.6
        if (nx, ny) in self_terr:
            s += 0.4
        if (nx, ny) in opp_terr:
            s += 0.9 if aggressive else 0.55

        adj_own = 0
        adj_opp = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                ax, ay = nx + adx, ny + ady
                if not inb(ax, ay) or (ax, ay) in obstacles:
                    continue
                if (ax, ay) in self_terr:
                    adj_own += 1
                elif (ax, ay) in opp_terr:
                    adj_opp += 1

        s += 0.22 * adj_own
        s -= (0.16 if not aggressive else 0.08) * adj_opp

        d_op = abs(nx - ox) + abs(ny - oy)
        s += (0.06 if aggressive else 0.035) * (14 - d_op)

        if s > best_score:
            best_score = s
            best = (nx, ny)

    return [best[0] - sx, best[1] - sy]