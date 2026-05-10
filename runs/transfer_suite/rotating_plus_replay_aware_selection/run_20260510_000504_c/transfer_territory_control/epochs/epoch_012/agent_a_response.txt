def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cell_score(x, y):
        if (x, y) in opp_terr:
            return 8.0
        if (x, y) in unclaimed:
            return 3.5
        if (x, y) in self_terr:
            return 1.0
        return 0.2

    cand_dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if unclaimed:
        cur_d_un = min(manh(sx, sy, ux, uy) for (ux, uy) in unclaimed)
    else:
        cur_d_un = 99
    # Prefer crossing towards opponent edge-adjacent cells
    edge_adj = []
    if opp_terr:
        for (px, py) in opp_terr:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    q = (px + dx, py + dy)
                    if inb(q[0], q[1]) and q not in opp_terr and q not in self_terr and q not in obstacles:
                        edge_adj.append(q)
        edge_adj = list(set(edge_adj))
    cur_d_edge = min((manh(sx, sy, ex, ey) for (ex, ey) in edge_adj), default=99)

    best = [0, 0]
    bestv = -10**18
    for dx, dy in cand_dirs:
        tx, ty = sx + dx, sy + dy
        if not inb(tx, ty) or (tx, ty) in obstacles:
            tx, ty = sx, sy
            dx, dy = 0, 0

        v = cell_score(tx, ty)
        if unclaimed:
            d_un = min(manh(tx, ty, ux, uy) for (ux, uy) in unclaimed)
            v += 0.30 * (cur_d_un - d_un)
        if edge_adj:
            d_edge = min(manh(tx, ty, ex, ey) for (ex, ey) in edge_adj)
            v += 0.20 * (cur_d_edge - d_edge)

        # Small tie-breaker: avoid getting stuck by preferring moves that reduce distance to opponent position
        ox, oy = observation["opponent_position"]
        v += -0.01 * manh(tx, ty, ox, oy)

        if v > bestv or (v == bestv and (dx, dy) < tuple(best)):
            bestv = v
            best = [dx, dy]
    return best