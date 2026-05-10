def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Predict opponent greedy next step to their nearest resource
    best_t = None
    best_td = None
    for rx, ry in resources:
        d = dist(ox, oy, rx, ry)
        if best_td is None or (d, rx, ry) < (best_td, best_t[0], best_t[1]):
            best_td = d
            best_t = (rx, ry)
    tx, ty = best_t

    def opp_next():
        bx, by = ox, oy
        bd = dist(ox, oy, tx, ty)
        for dx, dy in deltas:
            nx, ny = ox + dx, oy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            nd = dist(nx, ny, tx, ty)
            if (nd, nx, ny) < (bd, bx, by):
                bd, bx, by = nd, nx, ny
        return bx, by

    nxo, nyo = opp_next()

    # Score each candidate by how many resources we "win" vs opponent next step
    best_move = [0, 0]
    best_score = None
    res_sorted = sorted((r[0], r[1]) for r in resources)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0
        # Strongly prefer capturing any resource immediately
        for rx, ry in res_sorted:
            myd = dist(nx, ny, rx, ry)
            opd = dist(nxo, nyo, rx, ry)
            if myd == 0:
                score += 1000
            if myd < opd:
                score += 30
            elif myd == opd:
                score += 8
            # Encourage moving toward overall nearest
            score += -2 * myd
        # Small tiebreaker: prefer moves that also reduce distance to opponent target
        score += -dist(nx, ny, tx, ty) * 0.5
        if best_score is None or (score, -dx, -dy, nx, ny) > (best_score, -best_move[0], -best_move[1], sx + best_move[0], sy + best_move[1]):
            best_score = score
            best_move = [dx, dy]
    return best_move