def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    un = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    my = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(ox), int(oy)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    my_adj_dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    def adj8_to_my(x, y):
        for dx, dy in my_adj_dirs:
            if (x + dx, y + dy) in my:
                return True
        return False

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in my:
            s = -1
        else:
            s = 0
        if (nx, ny) in un:
            s += 6
        if adj8_to_my(nx, ny):
            s += 10
        if (nx, ny) in opp:
            s += 14
        dopp = abs(nx - ox) + abs(ny - oy)
        s += (28 - dopp) * (2 if (nx, ny) in opp or adj8_to_my(nx, ny) else 1)
        if (nx, ny) in un:
            s += 2
        if (nx, ny) == (ox, oy):
            s += 5
        if best is None or s > best_score or (s == best_score and (dx, dy) < best):
            best_score = s
            best = (dx, dy)

    return list(best if best is not None else (0, 0))