def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obs_list = observation.get("obstacles") or []
    obstacles = {(p[0], p[1]) for p in obs_list if p is not None and len(p) == 2}
    res_list = observation.get("resources") or []
    resources = [tuple(p) for p in res_list if p is not None and len(p) == 2 and (p[0], p[1]) not in obstacles]

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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    if not resources:
        tx = 0 if ox > sx else w - 1
        ty = 0 if oy > sy else h - 1
        best = None
        bestv = 10**18
        for dx, dy, nx, ny in legal:
            v = cheb(nx, ny, tx, ty) - 0.2 * cheb(nx, ny, ox, oy)
            if v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Pick a contested target: minimize (d_self - d_opp), tie by d_self
    best_t = None
    best_score = 10**18
    best_ds = 10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        score = ds - do
        if score < best_score or (score == best_score and ds < best_ds):
            best_score = score
            best_ds = ds
            best_t = (rx, ry)

    rx, ry = best_t
    best = None
    bestv = 10**18
    for dx, dy, nx, ny in legal:
        new_ds = cheb(nx, ny, rx, ry)
        new_do = cheb(nx, ny, ox, oy)
        # Primary: approach target. Secondary: widen distance from opponent.
        # Small deterministic bias to prefer staying if it doesn't worsen.
        v = new_ds - 0.35 * new_do + (0 if dx == 0 and dy == 0 else 0.01)
        if v < bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]