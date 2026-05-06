def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def block(x, y):
        return (x, y) in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_action_score(nx, ny):
        if block(nx, ny) or not inb(nx, ny):
            return -10**9
        if not resources:
            return -cheb(nx, ny, ox, oy)
        best_res = None
        best_my_d = 10**9
        best_margin = -10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            if myd < best_my_d:
                best_my_d = myd
                best_res = (rx, ry)
            margin = oppd - myd
            if margin > best_margin:
                best_margin = margin
        rx, ry = best_res
        myd = best_my_d
        oppd = cheb(ox, oy, rx, ry)

        # Prefer winning a reachable resource (margin > 0), but also keep distance from opponent.
        win_term = 50 * best_margin
        prox_term = -2 * cheb(nx, ny, ox, oy)
        resource_term = -3 * myd
        # Small tie-break toward resources opponent is far from
        opp_far_term = 0.5 * oppd
        return win_term + prox_term + resource_term + opp_far_term

    best_move = [0, 0]
    best_val = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            val = best_action_score(nx, ny)
            # Deterministic tie-break: prefer moves with smaller (dx,dy) lexicographically
            if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
                best_val = val
                best_move = [dx, dy]
    return best_move