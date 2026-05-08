def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set(observation.get("obstacles"))
    selfT = to_set(observation.get("self_territory"))
    res = to_set(observation.get("resources"))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_mv = (0, 0)
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        if res:
            dmin = min(abs(nx - x) + abs(ny - y) for (x, y) in res)
            dopp = abs(nx - ox) + abs(ny - oy)
            sc = -dmin * 1000 + (nx, ny in selfT) * 25 - dopp
        else:
            sc = -(abs(nx - ox) + abs(ny - oy)) * 1000 + (nx, ny in selfT) * 25
        if sc > best_sc or (sc == best_sc and (dx, dy) < best_mv):
            best_sc = sc
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]