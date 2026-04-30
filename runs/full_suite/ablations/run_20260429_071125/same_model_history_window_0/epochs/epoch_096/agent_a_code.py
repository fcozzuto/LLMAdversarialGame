def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]
    w, h = observation["grid_width"], observation["grid_height"]
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx*dx + dy*dy

    # Pick target resource that is relatively closer to us than to opponent.
    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            val = (do - ds)  # prefer resources opponent can't reach as quickly
            if best is None or val > best[0] or (val == best[0] and ds < best[1]):
                best = (val, ds, rx, ry)
        tx, ty = best[2], best[3]
    else:
        tx, ty = (w // 2), (h // 2)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            nx, ny = x, y  # engine keeps us in place
        dself = cheb(nx, ny, tx, ty)
        dopp = cheb(nx, ny, ox, oy)
        # Avoid getting stuck near obstacles: penalize moves that reduce escape options.
        neigh = 0
        for ex, ey in moves:
            ax, ay = nx + ex, ny + ey
            if in_bounds(ax, ay) and (ax, ay) not in obstacles:
                neigh += 1
        target = -dself + 0.35 * dopp + 0.15 * neigh
        # Minor preference to reduce distance to opponent if we are far (denies resources less safely).
        if cheb(x, y, ox, oy) > 20:
            target += -0.05 * cheb(nx, ny, ox, oy)
        if best_score is None or target > best_score:
            best_score = target
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]