def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy, nx, ny in legal:
            score = cheb(nx, ny, tx, ty)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    cx, cy = w // 2, h // 2
    res_list = [(r[0], r[1]) for r in resources]

    def best_resource_target(x, y):
        # Want to maximize lead over opponent: (opp_dist - my_dist).
        best_t = None
        best_key = None
        for rx, ry in res_list:
            myd = cheb(x, y, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            lead = opd - myd
            # tie-break: prefer closer and closer to center
            key = (lead, -myd, -(cheb(rx, ry, cx, cy)))
            if best_key is None or key > best_key:
                best_key = key
                best_t = (rx, ry)
        return best_t

    # Choose among moves by the resulting best lead, with tie-breakers.
    chosen = None
    chosen_key = None
    for dx, dy, nx, ny in legal:
        tx, ty = best_resource_target(nx, ny)
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        lead = opd - myd
        # Additional tie-break: maximize progress to target
        progress = -myd
        center_pref = -cheb(nx, ny, cx, cy)
        # Final tiny deterministic bias: direction ordering already fixed by legal loop
        key = (lead, progress, center_pref)
        if chosen_key is None or key > chosen_key:
            chosen_key = key
            chosen = (dx, dy)

    return [chosen[0], chosen[1]] if chosen else [0, 0]