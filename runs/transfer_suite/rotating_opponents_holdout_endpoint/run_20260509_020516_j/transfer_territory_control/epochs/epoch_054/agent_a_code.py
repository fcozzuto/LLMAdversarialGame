def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(v):
        s = set()
        for p in v or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < W and 0 <= y < H:
                    s.add((x, y))
        return s

    obstacles = to_set(observation.get("obstacles"))
    myT = to_set(observation.get("self_territory"))
    oppT = to_set(observation.get("opponent_territory"))
    unC = to_set(observation.get("unclaimed_cells"))
    res = to_set(observation.get("resources"))

    def inb(x, y): return 0 <= x < W and 0 <= y < H
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_op = abs(nx - ox) + abs(ny - oy)
        d_cur = abs(sx - ox) + abs(sy - oy)
        v = 0
        v += 200 if (nx, ny) in oppT else 0
        v += 80 if (nx, ny) in unC else 0
        v += 60 if (nx, ny) in res else 0
        v += 30 if (nx, ny) in myT else 0
        if d_op < d_cur:
            v += 40
        v -= 2 * d_op
        v -= 1 if (dx, dy) == (0, 0) else 0
        key = (v, -abs(dx), -abs(dy), dx, dy)
        if best is None or key > best:
            best = key
            bestv = (dx, dy)

    if bestv is not None:
        return [int(bestv[0]), int(bestv[1])]
    return [0, 0]