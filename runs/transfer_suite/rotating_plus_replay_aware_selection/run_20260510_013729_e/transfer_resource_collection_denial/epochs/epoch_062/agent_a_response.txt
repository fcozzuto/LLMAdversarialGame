def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}
    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0: dx = -dx
        dy = y2 - y1
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res_sorted = sorted(resources, key=lambda p: (p[0] * 8 + p[1], p[0], p[1]))

    def best_value(x, y):
        if (x, y) in obst:
            return -10**12
        best = -10**18
        for rx, ry in res_sorted:
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            cap = 3.5 if (x, y) == (rx, ry) else 0.0
            lead = do - ds  # positive if we are closer
            # Aggressive lead-seeking; slight anti-wander penalty
            val = cap + 2.2 * lead - 0.18 * ds - 0.06 * do
            if val > best:
                best = val
        return best

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        # 1-ply lookahead: choose our immediate move that creates best future position
        s1 = best_value(nx, ny)
        s2 = -0.02 * cheb(nx, ny, ox, oy)  # very small tie-break toward distancing from opponent
        score = s1 + s2
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    # If all moves blocked/unavailable, stay
    return best_move if best_score > -10**17 else [0, 0]