def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def to_set(key):
        s = set()
        for p in (observation.get(key) or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    self_t = to_set("self_territory")
    opp_t = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def score_cell(x, y):
        if not inb(x, y) or (x, y) in obstacles:
            return -10**9
        d_to_opp = abs(x - ox) + abs(y - oy)
        d_to_self = abs(x - sx) + abs(y - sy)
        if (x, y) in unclaimed:
            adj_self = any((nx, ny) in self_t for nx in (x-1, x, x+1) for ny in (y-1, y, y+1) if (nx, ny) != (x, y) and inb(nx, ny))
            adj_opp = any((nx, ny) in opp_t for nx in (x-1, x, x+1) for ny in (y-1, y, y+1) if (nx, ny) != (x, y) and inb(nx, ny))
            return 2000 + (500 if adj_self else 0) + (300 if adj_opp else 0) - 2*d_to_self + d_to_opp
        return -d_to_self + d_to_opp

    target_adj = []
    if unclaimed:
        for x, y in self_t:
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                    target_adj.append((nx, ny))
                    if len(target_adj) >= 8:
                        break
            if len(target_adj) >= 8:
                break

    if not target_adj and unclaimed:
        for x, y in opp_t:
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                    target_adj.append((nx, ny))
                    if len(target_adj) >= 8:
                        break
            if len(target_adj) >= 8:
                break

    best = (score_cell(sx, sy), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            sc = score_cell(nx, ny)
            if target_adj:
                sc += 10000 - min(abs(nx - tx) + abs(ny - ty) for tx, ty in target_adj)
            if sc > best[0]:
                best = (sc, dx, dy)
    return [int(best[1]), int(best[2])]