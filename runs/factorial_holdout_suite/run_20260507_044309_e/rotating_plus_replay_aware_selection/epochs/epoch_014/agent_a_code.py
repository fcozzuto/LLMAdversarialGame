def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def is_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        return [0, 0]

    cx, cy = w // 2, h // 2

    best_r = None
    best_val = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Opponent greedily moves one step toward (rx,ry)
        step_x = 0 if rx == ox else (1 if rx > ox else -1)
        step_y = 0 if ry == oy else (1 if ry > oy else -1)
        pnx, pny = ox + step_x, oy + step_y
        opp_block = 2.0 if (not is_free(pnx, pny)) else 0.0

        # Prefer resources we can reach first; tie-break: farther from center (to disturb paths),
        # then smaller opponent distance (avoid giving them alternatives).
        val = (do - ds) + opp_block
        tieb = (abs(rx - cx) + abs(ry - cy), do, ds)
        if best_val is None or val > best_val or (val == best_val and tieb < best_tieb):
            best_val = val
            best_tieb = tieb
            best_r = (rx, ry)

    rx, ry = best_r
    cur_d = cheb(sx, sy, rx, ry)
    best_move = (0, 0)
    best_mscore = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not is_free(nx, ny):
            continue
        nd = cheb(nx, ny, rx, ry)
        # Secondary: keep advantage against that same target, and slightly prefer moving toward center
        n_do = cheb(ox, oy, rx, ry)
        mscore = (cur_d - nd) + 0.01 * (abs(ox - nx) - abs(ox - sx)) + 0.001 * (-(abs(nx - cx) + abs(ny - cy)))
        if best_mscore is None or mscore > best_mscore:
            best_mscore = mscore
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]