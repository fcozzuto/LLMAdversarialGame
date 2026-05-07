def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def utility(posx, posy):
        if not resources:
            cx, cy = (gw - 1) // 2, (gh - 1) // 2
            return -cheb(posx, posy, cx, cy)
        best = -10**18
        for rx, ry in resources:
            if (rx, ry) == (posx, posy):
                return 10**6
            our_d = cheb(posx, posy, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach earlier than opponent; add small tie-break to be closer.
            v = (opp_d - our_d) * 100 + (gw + gh - our_d)
            if v > best:
                best = v
        return best

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = utility(nx, ny)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]