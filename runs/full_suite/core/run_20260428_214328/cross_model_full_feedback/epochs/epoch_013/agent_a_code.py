def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inside(x, y)) or ((x, y) in obs)

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        ay = y1 - y2
        return ax if ax >= 0 else -ax if ay >= 0 else -ay

    def cd(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    best_move = (0, 0)
    best_eval = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        if res:
            # Choose the resource that we can "beat" (small our_dist - opp_dist); if tie, closest for us.
            best_r = None
            best_r_key = None
            for rx, ry in res:
                od = cd(nx, ny, rx, ry)  # our dist if going to r from nx,ny
                pd = cd(ox, oy, rx, ry)
                key = (od - pd, od, rx, ry)
                if best_r_key is None or key < best_r_key:
                    best_r_key = key
                    best_r = (rx, ry)
            eval_key = (best_r_key[0], best_r_key[1], dx, dy)
        else:
            # No resources: move to reduce distance to opponent.
            eval_key = (cd(nx, ny, ox, oy), -nx, -ny, dx, dy)
        if best_eval is None or eval_key < best_eval:
            best_eval = eval_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]