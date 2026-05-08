def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if v:
            for p in v:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))
    unclaimed = toset(observation.get("unclaimed_cells"))

    if not unclaimed and resources:
        unclaimed = set(resources)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    bestv = -10**18

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        if (nx, ny) in unclaimed:
            val += 100000
        if (nx, ny) in resources:
            val += 60000
        if (nx, ny) in selfT:
            val += 2000
        if (nx, ny) in oppT:
            val -= 3000

        adj_self = False
        adj_opp = False
        adj_un = False
        for ddx, ddy in dirs:
            ax, ay = nx + ddx, ny + ddy
            if not inside(ax, ay):
                continue
            if (ax, ay) in selfT:
                adj_self = True
            if (ax, ay) in oppT:
                adj_opp = True
            if (ax, ay) in unclaimed:
                adj_un = True

        if adj_self:
            val += 1500
        if adj_un:
            val += 2500
        if adj_opp:
            val -= 800

        # Nudge toward unclaimed; otherwise toward opponent to gain advantage.
        if unclaimed or resources:
            targets = unclaimed if unclaimed else resources
            if targets:
                md = 10**9
                for tx, ty in targets:
                    d = abs(tx - nx) + abs(ty - ny)
                    if d < md:
                        md = d
                val += -md
        else:
            val += -(abs(ox - nx) + abs(oy - ny)) * 2

        # Deterministic tie-breaker: prefer staying if equal, else smaller dx, then smaller dy
        if val > bestv or (val == bestv and (best is None or (dx, dy) < tuple(best))):
            bestv = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best