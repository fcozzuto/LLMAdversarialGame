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

    opp_pos = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def adj_unclaimed(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in unclaimed:
                        return True
        return False

    un_list = list(unclaimed) if unclaimed else []
    def nearest_un_dist(x, y):
        if not un_list:
            return abs(x - (w - 1)) + abs(y - (h - 1))
        best = 10**9
        for tx, ty in un_list:
            d = abs(tx - x) + abs(ty - y)
            if d < best:
                best = d
        return best

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            val = -10**12
        else:
            base = 0
            if (nx, ny) in selfT:
                base = 5
            elif (nx, ny) in unclaimed:
                base = 12
            elif (nx, ny) in oppT:
                base = 8
            a = 3 if adj_unclaimed(nx, ny) else 0
            d_un = nearest_un_dist(nx, ny)
            d_opp = abs(nx - ox) + abs(ny - oy)
            val = base + a - 1.5 * d_un + 0.05 * d_opp
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]