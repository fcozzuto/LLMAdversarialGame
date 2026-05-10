def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def neigh(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    yield x + dx, y + dy

    # Frontier / pressure heuristic
    opp_cx = ox
    opp_cy = oy
    if opp_terr:
        sxm = sum(p[0] for p in opp_terr) / len(opp_terr)
        sym = sum(p[1] for p in opp_terr) / len(opp_terr)
        opp_cx, opp_cy = sxm, sym

    def cell_score(tx, ty):
        if (tx, ty) in obstacles:
            return -10**9
        d = manh(sx, sy, tx, ty)
        od = manh(int(round(opp_cx)), int(round(opp_cy)), tx, ty)
        adj_self = 0
        adj_opp = 0
        for nx, ny in neigh(tx, ty):
            if (nx, ny) in self_terr:
                adj_self += 1
            if (nx, ny) in opp_terr:
                adj_opp += 1
        # Prefer expanding frontiers, but keep distance from opponent territory
        return (0.85 * od) - (1.05 * d) + (2.0 * adj_self) - (2.25 * adj_opp)

    best = None
    bestv = -10**18
    for tx, ty in unclaimed:
        v = cell_score(tx, ty)
        if v > bestv or (v == bestv and (tx < best[0] or (tx == best[0] and ty < best[1]))):
            bestv = v
            best = (tx, ty)

    if best is None:
        return [0, 0]
    tx, ty = best

    # Choose among valid immediate moves by local improvement
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    bestm = (0, 0)
    bestmv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Reward moving closer to target; also prefer stepping into promising frontier
        v = (-manh(nx, ny, tx, ty)) * 1.2 + (0.3 * cell_score(nx, ny))
        if v > bestmv or (v == bestmv and (dx, dy) < bestm):
            bestmv = v
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]