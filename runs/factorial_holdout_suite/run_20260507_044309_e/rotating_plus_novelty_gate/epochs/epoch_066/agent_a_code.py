def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if not inb(sx, sy):
        return [0, 0]
    if not resources:
        return [0, 0]

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    best_move = None
    best_val = None
    best_detail = None

    for dx, dy, nx, ny in valid:
        my_d0 = cheb(nx, ny, ox, oy)  # helps avoid getting too far behind
        best_r_val = None
        best_r_detail = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Primary: contest (higher means I am closer than opp)
            contest = opd - myd
            # Secondary: prefer immediate capture, then nearer targets
            immediate = 3 if (nx == rx and ny == ry) else 0
            val = contest + immediate - 0.01 * myd + 0.001 * my_d0
            detail = (opd - myd, immediate, -myd, rx, ry)
            if best_r_val is None or val > best_r_val or (val == best_r_val and detail > best_r_detail):
                best_r_val = val
                best_r_detail = detail
        if best_r_val is None:
            continue
        move_detail = (best_r_detail[0], best_r_detail[1], best_r_detail[2], dx, dy)
        if best_val is None or best_r_val > best_val or (best_r_val == best_val and move_detail > best_detail):
            best_val = best_r_val
            best_detail = move_detail
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]