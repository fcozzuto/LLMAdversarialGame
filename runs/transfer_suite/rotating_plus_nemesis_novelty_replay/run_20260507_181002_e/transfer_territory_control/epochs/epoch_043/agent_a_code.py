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
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    oppT = toset(observation.get("opponent_territory"))
    myT = toset(observation.get("self_territory"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    nearest_res = None
    if resources:
        bestd = 10**9
        for rx, ry in resources:
            d = abs(rx - sx) + abs(ry - sy)
            if d < bestd:
                bestd = d
                nearest_res = (rx, ry)
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = 0
        if (nx, ny) in oppT:
            sc += 50
        if (nx, ny) in myT:
            sc -= 2
        if (nx, ny) in unclaimed:
            sc += 8
        if resources:
            if nearest_res is not None:
                sc += -2 * (abs(nx - nearest_res[0]) + abs(ny - nearest_res[1]))
            if (nx, ny) in resources:
                sc += 40
        sc += - (abs(nx - ox) + abs(ny - oy))  # approach opponent
        if (nx, ny) in oppT or (nx, ny) in unclaimed:
            sc += 3
        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]