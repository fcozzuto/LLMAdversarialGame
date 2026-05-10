def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs + [(0, 0)]:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        nd_self = 10**9
        for rx, ry in res:
            d = abs(nx - rx) + abs(ny - ry)
            if d < nd_self:
                nd_self = d
        nd_opp = abs(nx - ox) + abs(ny - oy)
        val = -nd_self + 0.35 * nd_opp
        if nd_self == 0:
            val += 1000000
        if (dx, dy) == (0, 0):
            val -= 0.5
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]