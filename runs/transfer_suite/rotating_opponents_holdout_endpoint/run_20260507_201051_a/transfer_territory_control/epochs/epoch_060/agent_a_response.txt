def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        t = (nx, ny)
        if t in oppT:
            cell = 7
        elif t in unclaimed:
            cell = 4
        elif t in selfT:
            cell = -2
        else:
            cell = 1

        dist_opp = abs(nx - ox) + abs(ny - oy)
        dist_cent = abs(nx - cx) + abs(ny - cy)

        # Local frontier pressure: prefer moves near opponent/unclaimed to expand.
        near_opp = 0
        near_un = 0
        for ax, ay in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            px, py = nx + ax, ny + ay
            if not inside(px, py) or (px, py) in obstacles:
                continue
            if (px, py) in oppT:
                near_opp += 1
            if (px, py) in unclaimed:
                near_un += 1

        # If we're not close enough to contest, drift toward center line then opponent.
        center_drive = -0.6 * dist_cent
        if abs(nx - ox) + abs(ny - oy) <= 3:
            center_drive *= 1.6

        # Prefer moves that reduce distance to opponent slightly when they're nearby.
        opp_drive = -1.2 * dist_opp if (abs(nx - ox) + abs(ny - oy) <= 6) else -0.3 * dist_opp

        score = cell * 1000 + near_opp * 120 + near_un * 35 + center_drive + opp_drive

        # Tiny deterministic tie-breaker by move direction ordering.
        tie = dirs.index((dx, dy))
        cand = (score, -near_opp, -near_un, -dist_opp, tie, dx, dy)
        if cand > best:
            best = cand

    return [int(best[-2]), int(best[-1])]