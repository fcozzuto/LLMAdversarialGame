def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = observation.get("obstacles") or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles}

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

    resources = observation.get("resources") or []
    res = [(int(p[0]), int(p[1])) for p in resources]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            valid.append((dx, dy, nx, ny))

    if not valid:
        return [0, 0]

    if res:
        best_r = None
        best_key = None
        for rx, ry in res:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # prefer resources we can reach sooner and where opponent is disadvantaged
            key = (-(od - sd) * 100 + sd * 2, sd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)

        rx, ry = best_r
        best_mv = None
        best_val = None
        best_lex = None
        for dx, dy, nx, ny in valid:
            on_r = (nx, ny) == (rx, ry)
            dist = cheb(nx, ny, rx, ry)
            opp_d = cheb(nx, ny, ox, oy)
            # prioritize collecting, then approaching contested resource, lightly discouraging being too far from opponent
            val = (100000 if on_r else 0) - dist * 5 + (max(0, cheb(ox, oy, rx, ry) - dist) * 2) - opp_d * 0.1
            lex = (dx, dy)
            if best_val is None or val > best_val or (val == best_val and lex < best_lex):
                best_val = val
                best_mv = (dx, dy)
                best_lex = lex
        return [int(best_mv[0]), int(best_mv[1])]

    # No resources: deterministically approach opponent (or stay if blocked)
    best_mv = None
    best_val = None
    best_lex = None
    for dx, dy, nx, ny in valid:
        d = cheb(nx, ny, ox, oy)
        val = -d
        lex = (dx, dy)
        if best_val is None or val > best_val or (val == best_val and lex < best_lex):
            best_val = val
            best_mv = (dx, dy)
            best_lex = lex
    return [int(best_mv[0]), int(best_mv[1])]