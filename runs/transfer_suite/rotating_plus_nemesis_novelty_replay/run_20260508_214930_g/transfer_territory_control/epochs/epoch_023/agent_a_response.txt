def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_count(x, y, sset):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in sset:
                        c += 1
        return c

    def edge_pen(x, y):
        return (min(x, w - 1 - x) + min(y, h - 1 - y))

    best_target = None
    best_dist = None
    for (ux, uy) in unclaimed:
        if adj_count(ux, uy, opp_t) > 0 and inside(ux, uy):
            d = abs(ux - sx) + abs(uy - sy)
            if best_dist is None or d < best_dist:
                best_dist = d
                best_target = (ux, uy)
    if best_target is None:
        for (ux, uy) in unclaimed:
            if inside(ux, uy):
                d = abs(ux - sx) + abs(uy - sy)
                if best_dist is None or d < best_dist:
                    best_dist = d
                    best_target = (ux, uy)

    tx, ty = best_target if best_target is not None else (sx, sy)

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        a_self = adj_count(nx, ny, self_t)
        a_opp = adj_count(nx, ny, opp_t)
        dist = abs(nx - tx) + abs(ny - ty)
        val = 0
        if (nx, ny) in self_t:
            val = 6 + 1.5 * a_self + 0.1 * edge_pen(nx, ny) - 0.01 * dist
        elif (nx, ny) in opp_t:
            val = 14 + 2.0 * a_self + 0.5 * a_opp + 0.1 * edge_pen(nx, ny) - 0.01 * dist
        else:
            if (nx, ny) in unclaimed:
                val = 4 + 1.3 * a_self + 1.0 * a_opp + 0.1 * edge_pen(nx, ny) - 0.02 * dist
            else:
                val = 1 + 0.7 * a_self + 0.4 * a_opp + 0.05 * edge_pen(nx, ny) - 0.02 * dist
        if val > best_score:
            best_score = val
            best_move = [dx, dy]
    return best_move