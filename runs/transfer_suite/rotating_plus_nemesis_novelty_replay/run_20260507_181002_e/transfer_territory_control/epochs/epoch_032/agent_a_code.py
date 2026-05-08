def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def near_opp(x, y):
        return abs(x - ox) <= 1 and abs(y - oy) <= 1

    best = (-10**18, (0, 0))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        dcenter = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        dopp = abs(nx - ox) + abs(ny - oy)
        dist_self = abs(nx - sx) + abs(ny - sy)

        # Territory value
        if (nx, ny) in selfT:
            gain = 2.0
        elif (nx, ny) in oppT:
            # Only take it if it helps us secure toward the center (deterministic deterrence)
            gain = 3.5 if dcenter < (sx - cx) * (sx - cx) + (sy - cy) * (sy - cy) else -2.5
        elif (nx, ny) in unclaimed:
            gain = 4.0
        else:
            gain = 0.5

        # Avoid immediate contests near opponent's position
        contest = -3.0 if near_opp(nx, ny) and (nx, ny) not in selfT else 0.0

        # Prefer moves that reduce distance to center and opponent
        score = gain * 10.0 + contest * 1.0 - dcenter * 0.15 - dopp * 0.45 + dist_self * (-0.05)
        if score > best[0]:
            best = (score, (dx, dy))

    return [int(best[1][0]), int(best[1][1])]