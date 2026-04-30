def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_cell(x, y):
        if (x, y) in occ:
            return -10**18
        my_to_opp = cheb(x, y, ox, oy)
        best_lead = -10**18
        best_tie = 10**18
        any_res = False
        for rx, ry in resources:
            any_res = True
            myd = cheb(x, y, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            lead = opd - myd  # positive means we are closer than opponent
            if lead > best_lead or (lead == best_lead and myd < best_tie):
                best_lead = lead
                best_tie = myd
        if not any_res:
            tx, ty = (w - 1) // 2, (h - 1) // 2
            return -cheb(x, y, tx, ty)
        # If we can get ahead (positive lead), prioritize finishing earlier and staying away from opponent.
        # If we are behind (non-positive lead), reduce the loss by minimizing how far we trail, and keep distance from opponent.
        finish = min(cheb(x, y, rx, ry) for rx, ry in resources) if resources else 0
        return best_lead * 1000 - best_tie * 5 - my_to_opp * (2 if best_lead > 0 else 1) - finish

    best = (0, 0)
    bestv = -10**18
    # Deterministic tie-break by lexicographic order of delta list already fixed.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        v = score_cell(nx, ny)
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]