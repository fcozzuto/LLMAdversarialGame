def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a resource by "race advantage": lower (my_dist - opp_dist) first.
    best_r = None
    best_delta = None
    best_my = None
    for rx, ry in res:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        delta = myd - opd
        if best_r is None or delta < best_delta or (delta == best_delta and myd < best_my) or (delta == best_delta and myd == best_my and (rx, ry) < best_r):
            best_r = (rx, ry)
            best_delta = delta
            best_my = myd
    tx, ty = best_r

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best_move = (0, 0)
    best_score = None
    # Maximize advantage: my_dist_next - 0.5*opp_dist_next (lower is better for me).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Opponent may also move; approximate by assuming they reduce their own distance by 1 cell in Chebyshev.
        opd_next = opd - 1 if opd > 0 else 0
        score = myd - 0.5 * opd_next
        # Small tie-breakers: prefer progress and staying away from opponent.
        score2 = score * 1000 + myd * 10 + cheb(nx, ny, ox, oy)
        if best_score is None or score2 < best_score or (score2 == best_score and (dx, dy) < best_move):
            best_score = score2
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]