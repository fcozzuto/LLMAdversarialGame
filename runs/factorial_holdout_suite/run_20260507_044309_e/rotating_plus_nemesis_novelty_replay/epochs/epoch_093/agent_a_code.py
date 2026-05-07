def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return (x, y) in obstacles

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    best = None
    best_delta = -10**18
    best_ds = 10**18
    best_pos = (10**18, 10**18)
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        delta = do - ds
        if delta > best_delta or (delta == best_delta and (ds < best_ds or (ds == best_ds and ((rx, ry) < best_pos)))):
            best_delta = delta
            best_ds = ds
            best_pos = (rx, ry)
            best = (rx, ry)

    rx, ry = best

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_m = (0, 0)
    best_score = -10**18
    best_md = 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        nds = cheb(nx, ny, rx, ry)
        ndo = cheb(ox, oy, rx, ry)
        score = ndo - nds
        if score > best_score or (score == best_score and (nds < best_md or (nds == best_md and (dx, dy) < best_m))):
            best_score = score
            best_md = nds
            best_m = (dx, dy)

    if best_m == (0, 0):
        # If all adjacent are blocked/out of bounds, just stay.
        return [0, 0]
    return [best_m[0], best_m[1]]