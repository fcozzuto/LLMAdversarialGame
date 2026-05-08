def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def eval_from(px, py):
        best_s = 10**18
        have = False
        for rx, ry in resources:
            if not valid(rx, ry):
                continue
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            have = True
            # Strongly prefer resources we can reach first or tie; then closeness.
            if do < ds:
                s = 10**6 + (ds - do) * 10 + ds
            elif do == ds:
                s = ds * 2 - 1
            else:
                s = ds - (do - ds)
            if s < best_s:
                best_s = s
        if not have:
            # Fallback: move toward center
            cx = (w - 1) // 2
            cy = (h - 1) // 2
            return cheb(px, py, cx, cy) + cheb(ox, oy, cx, cy) * 0
        return best_s

    best_move = (0, 0)
    best_val = 10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = eval_from(nx, ny)
        if v < best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]