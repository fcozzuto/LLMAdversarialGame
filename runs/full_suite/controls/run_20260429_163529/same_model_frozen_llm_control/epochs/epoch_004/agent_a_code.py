def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    best_target = None; best_val = None
    def dist(a, b, c, d):
        dx = a - c; dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev (diagonal move cost)
    for rx, ry in resources:
        if (rx, ry) == (sx, sy) or (rx, ry) in obstacles:
            continue
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        val = ds - 0.7 * do  # prefer resources we're relatively closer to
        if best_val is None or val < best_val:
            best_val = val; best_target = (rx, ry)
    if best_target is None:
        return [0, 0]
    rx, ry = best_target
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    best_move = (0, 0); best_score = None
    for dx, dy in moves:
        nx = sx + dx; ny = sy + dy
        if not inb(nx, ny):
            continue
        # slight incentive to approach and to reduce opponent distance to same target
        d1 = dist(nx, ny, rx, ry)
        d2 = dist(ox, oy, rx, ry)
        score = d1 - 0.25 * d2
        # break ties by preferring moves that reduce distance to opponent as a secondary option
        if d1 == d1:  # keep deterministic
            opp = dist(nx, ny, ox, oy)
            score2 = score + 0.01 * opp
        else:
            score2 = score
        if best_score is None or score2 < best_score:
            best_score = score2; best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]