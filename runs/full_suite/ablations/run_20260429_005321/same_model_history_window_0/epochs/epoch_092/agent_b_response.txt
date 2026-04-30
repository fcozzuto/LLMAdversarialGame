def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    def eval_pos(px, py):
        if not inb(px, py) or (px, py) in obstacles:
            return -10**9
        if not resources:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center_dist = abs(px - cx) + abs(py - cy)
            return -center_dist - 0.3 * cheb(px, py, ox, oy)
        best = -10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ps = cheb(px, py, rx, ry)
            os_ = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; penalize if opponent is faster.
            val = (os_ - ps) * 12 - ps * 2
            # Encourage moving toward resources while staying away from immediate danger.
            val -= 0.6 * cheb(px, py, ox, oy)
            if val > best:
                best = val
        return best

    deltas = (-1, 0, 1)
    best_move = [0, 0]
    best_score = -10**18
    # Deterministic tie-break: lexicographic over (dx, dy) order.
    for dx in deltas:
        for dy in deltas:
            nx, ny = sx + dx, sy + dy
            sc = eval_pos(nx, ny)
            if sc > best_score:
                best_score = sc
                best_move = [dx, dy]
            elif sc == best_score:
                if [dx, dy] < best_move:
                    best_move = [dx, dy]
    return best_move