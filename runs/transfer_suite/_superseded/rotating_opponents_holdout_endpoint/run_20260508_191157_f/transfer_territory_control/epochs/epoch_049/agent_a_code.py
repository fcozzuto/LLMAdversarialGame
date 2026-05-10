def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    neigh8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    opp_set = set()
    self_set = set()
    for p in opp_terr:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                opp_set.add((x, y))
    for p in self_terr:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                self_set.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    cx, cy = w // 2, h // 2

    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(ox), int(oy)

    best = None
    best_sc = None

    for cell in unclaimed:
        if not (isinstance(cell, (list, tuple)) and len(cell) >= 2):
            continue
        x, y = int(cell[0]), int(cell[1])
        if not inb(x, y):
            continue
        adj_opp = 0
        adj_self = 0
        near_block = 0
        for dx, dy in neigh8:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in blocked:
                if dx != 0 or dy != 0:
                    near_block += 1
            if (nx, ny) in opp_set:
                adj_opp += 1
            if (nx, ny) in self_set:
                adj_self += 1
        sc = adj_opp * 7 + adj_self * 3 - (abs(x - ox) + abs(y - oy)) - near_block * 2 - (abs(x - cx) + abs(y - cy)) * 0.05
        if best_sc is None or sc > best_sc or (sc == best_sc and (abs(x - sx) + abs(y - sy) < abs(best[0] - sx) + abs(best[1] - sy))):
            best_sc = sc
            best = (x, y)

    if best is None:
        tx, ty = cx, cy
    else:
        tx, ty = best

    best_move = [0, 0]
    best_dist = None
    for dx, dy in neigh8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) and (nx, ny) != (sx, sy):
            continue
        d = abs(nx - tx) + abs(ny - ty)
        if best_dist is None or d < best_dist or (d == best_dist and (dx, dy) < (best_move[0], best_move[1])):
            best_dist = d
            best_move = [dx, dy]
    return best_move