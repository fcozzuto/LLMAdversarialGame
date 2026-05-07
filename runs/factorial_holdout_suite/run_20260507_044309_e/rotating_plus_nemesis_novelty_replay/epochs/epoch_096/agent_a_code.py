def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    res = observation.get("resources") or []
    resources = res if isinstance(res, (list, tuple)) else []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blk(x, y):
        return (x, y) in obstacles

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = (-(10**18), 10**18, 0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blk(nx, ny):
            nx, ny = sx, sy

        bestv = -(10**18)
        bestd = 10**18
        for rx, ry in resources:
            ds = cd(nx, ny, rx, ry)
            do = cd(ox, oy, rx, ry)
            v = (do - ds) * 12 - ds
            if nx == rx and ny == ry:
                v += 10**6
            if v > bestv or (v == bestv and ds < bestd):
                bestv, bestd = v, ds

        dself = cd(nx, ny, ox, oy)
        cand = (bestv, dself if dself < best[1] else best[1], dx, dy)
        if cand[0] > best[0] or (cand[0] == best[0] and cand[1] < best[1]):
            best = (cand[0], cand[1], dx, dy)

    return [int(best[2]), int(best[3])]