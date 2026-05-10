def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_ter = set(tuple(p) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_ter = set(tuple(p) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    neigh8 = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def mindist_to_set(x, y, s):
        if not s:
            return 99
        md = 99
        for a, b in s:
            d = abs(a - x) + abs(b - y)
            if d < md:
                md = d
                if md == 0:
                    break
        return md

    best = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in self_ter:
            cell_score = 2
        elif (nx, ny) in unclaimed:
            cell_score = 10
        elif (nx, ny) in opp_ter:
            cell_score = 8
        else:
            cell_score = 4

        adj_self = 0
        adj_opp = 0
        for ddx, ddy in neigh8:
            tx, ty = nx + ddx, ny + ddy
            if (tx, ty) in self_ter:
                adj_self += 1
            if (tx, ty) in opp_ter:
                adj_opp += 1

        d_un = mindist_to_set(nx, ny, unclaimed)
        d_opp = mindist_to_set(nx, ny, opp_ter)

        score = cell_score
        score += 0.6 * adj_self
        score += 0.4 * adj_opp
        score += -0.9 * d_un
        score += -0.25 * d_opp
        score += -0.05 * (abs(nx - ox) + abs(ny - oy))

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]