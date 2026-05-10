def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles if p and len(p) == 2}
    self_terr = {(p[0], p[1]) for p in (observation.get("self_territory") or []) if p and len(p) == 2}
    opp_terr = {(p[0], p[1]) for p in (observation.get("opponent_territory") or []) if p and len(p) == 2}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or []) if p and len(p) == 2}

    opp_cx, opp_cy = (w - 1, h - 1)
    if opp_terr:
        opp_cx = sum(x for x, y in opp_terr) // len(opp_terr)
        opp_cy = sum(y for x, y in opp_terr) // len(opp_terr)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_target():
        # Prefer unclaimed near opponent; else aim at opponent centroid.
        if unclaimed:
            tx, ty = opp_cx, opp_cy
            best = None
            for x, y in unclaimed:
                d = abs(x - tx) + abs(y - ty)
                if best is None or d < best[0] or (d == best[0] and (x, y) < (best[1], best[2])):
                    best = (d, x, y)
            return best[1], best[2]
        return opp_cx, opp_cy

    tx, ty = best_target()

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def adj_to_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in opp_terr:
                    return True
        return False

    def score_cell(x, y):
        if (x, y) in obs:
            return -10**9
        sc = 0.0
        if (x, y) in opp_terr:
            sc += 5.0  # likely flip
        if (x, y) in self_terr:
            sc -= 0.2  # already ours; expansion still possible elsewhere
        if (x, y) in unclaimed:
            sc += 1.2
        if (x, y) in opp_terr or adj_to_opp(x, y):
            sc += 2.0
        # Move toward a good target (mostly deterministic)
        sc += 1.0 * (-(abs(x - tx) + abs(y - ty)))
        # Avoid drifting away from center early if unclaimed scarce
        sc += 0.1 * (-(abs(x - opp_cx) + abs(y - opp_cy)))
        return sc

    best_move = (0, 0)
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        sc = score_cell(nx, ny)
        # Tie-break deterministically: prefer smallest dx, then dy
        if sc > best_sc or (sc == best_sc and (dx, dy) < best_move):
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]