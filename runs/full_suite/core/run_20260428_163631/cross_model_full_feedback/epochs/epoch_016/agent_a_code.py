def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        try:
            x, y = p
            obst.add((int(x), int(y)))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        try:
            x, y = r
            x, y = int(x), int(y)
        except:
            continue
        if inb(x, y) and (x, y) not in obst:
            res.append((x, y))

    cand_moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_key = None
    for dx, dy in cand_moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        if res:
            mk = None
            for rx, ry in res:
                myd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                adv = od - myd
                key = (-adv, myd, rx + ry)
                if mk is None or key < mk:
                    mk = key
            key = mk
        else:
            myd = cheb(nx, ny, ox, oy)
            key = (myd, nx + ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]