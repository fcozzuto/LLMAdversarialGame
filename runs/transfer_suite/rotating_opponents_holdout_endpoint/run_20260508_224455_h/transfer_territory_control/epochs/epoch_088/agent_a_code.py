def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    def to_set(lst):
        s = set()
        for p in lst or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set(observation.get("obstacles"))
    selfT = to_set(observation.get("self_territory"))
    oppT = to_set(observation.get("opponent_territory"))
    unclaimed = to_set(observation.get("unclaimed_cells"))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    # nearest unclaimed for shaping
    if unclaimed:
        best_un_d = 10**9
        best_un = (sx, sy)
        for tx, ty in unclaimed:
            d = abs(tx - sx) + abs(ty - sy)
            if d < best_un_d:
                best_un_d = d
                best_un = (tx, ty)
    else:
        best_un_d = 0
        best_un = (sx, sy)

    def adj_unclaimed(x, y):
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax or ay:
                    if (x + ax, y + ay) in unclaimed:
                        return True
        return False

    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        s = 0
        if (x, y) in selfT:
            s += 6
        if (x, y) in unclaimed:
            s += 9 + (2 if adj_unclaimed(x, y) else 0)
        if (x, y) in oppT:
            # flipping on entry is enabled; prioritize capturing edge/boundary
            s += 7 + (3 if adj_unclaimed(x, y) else 0)
            s += 2 if (abs(x - sx) + abs(y - sy) <= 3) else 0

        d = abs(x - best_un[0]) + abs(y - best_un[1])
        s += (best_un_d - d) * 1.5
        return s

    # fixed preference order for determinism: diagonals then cardinals then stay
    candidates = [(-1, -1), (-1, 1), (1, -1), (1, 1), (0, -1), (-1, 0), (1, 0), (0, 1), (0, 0)]
    best_move = (0, 0)
    best_s = -10**18
    for dx, dy in candidates:
        x, y = sx + dx, sy + dy
        if not inside(x, y):
            continue
        s = score_cell(x, y)
        if s > best_s:
            best_s = s
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]