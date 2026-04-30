def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    ax, ay = (w - 1) // 2, (h - 1) // 2
    if not resources:
        tx, ty = ax, ay
    else:
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in occ:
                continue
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            md = cheb(rx, ry, ax, ay)
            # Prioritize resources we are closer to than opponent; also favor central ones to contest.
            key = (-(od - sd), sd, -md, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best if best is not None else (ax, ay)

    # Move toward chosen target while avoiding obstacles and staying out of opponent overlap.
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        if (nx, ny) == (ox, oy):
            continue
        dist = cheb(nx, ny, tx, ty)
        # Slightly bias away from opponent to reduce contest losses near them.
        opp_bias = cheb(nx, ny, ox, oy)
        # Prefer actions that reduce our distance to target; tiebreaker: increase opp_bias.
        key = (dist, -opp_bias, (dx != 0 or dy != 0), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]