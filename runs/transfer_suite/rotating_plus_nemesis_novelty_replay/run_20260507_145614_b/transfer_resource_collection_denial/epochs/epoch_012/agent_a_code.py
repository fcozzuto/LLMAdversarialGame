def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_target(rx, ry):
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        if do < ds: 
            return 10**6 + (ds - do)  # discourage targets opponent can reach first
        return (ds * 2) + (do - ds)  # deterministic tie-break via distance structure

    best_r = None
    best_s = 10**18
    for i in range(len(resources)):
        rx, ry = resources[i]
        if not valid(rx, ry):
            continue
        s = score_target(rx, ry)
        if s < best_s or (s == best_s and (rx, ry) < best_r):
            best_s = s
            best_r = (rx, ry)

    if best_r is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_r

    best = None
    best_step = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        s = cheb(nx, ny, tx, ty)
        if best is None or s < best or (s == best and (dx, dy) < best_step):
            best = s
            best_step = (dx, dy)

    if best_step is None:
        return [0, 0]
    return [int(best_step[0]), int(best_step[1])]