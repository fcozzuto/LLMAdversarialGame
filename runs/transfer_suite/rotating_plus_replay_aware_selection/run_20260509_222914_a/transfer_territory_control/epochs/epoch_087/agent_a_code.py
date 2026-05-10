def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    self_ter = set(tuple(p) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_ter = set(tuple(p) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh = dirs

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_counts(x, y):
        a_self = a_opp = a_un = 0
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in self_ter:
                a_self += 1
            if (nx, ny) in opp_ter:
                a_opp += 1
            if (nx, ny) in unclaimed:
                a_un += 1
        return a_self, a_opp, a_un

    def nearest_unclaimed_dist(x, y):
        if not unclaimed:
            return 999
        best = 999
        for ux, uy in unclaimed:
            d = abs(ux - x) + abs(uy - y)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    base_d = nearest_unclaimed_dist(sx, sy)

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        a_self, a_opp, a_un = adj_counts(nx, ny)
        val = 0

        if (nx, ny) in opp_ter:
            val += 24 + 2 * a_self - 1 * a_opp
        elif (nx, ny) in unclaimed:
            val += 12 + 2 * a_self - 1 * a_opp
        elif (nx, ny) in self_ter:
            val += 3 + 1 * a_self + 1 * a_un - 2 * a_opp
        else:
            val += 1 + 1 * a_self + a_un - 1 * a_opp

        nd = nearest_unclaimed_dist(nx, ny)
        val += 0.8 * (base_d - nd)

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    if best_move == [0, 0] and (sx, sy) in obstacles:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
    return best_move