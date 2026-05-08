def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    self_pos = (x, y)
    opp_pos = (ox, oy)

    if resources:
        best_r = None
        best_key = None
        for r in resources:
            if r in obstacles:
                continue
            rx, ry = r
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we can get to it first; break ties deterministically.
            key = (do - ds, ds, rx, ry)
            if best_key is None or key < best_key:
                best_key, best_r = key, r
        if best_r is None:
            target = (w // 2, h // 2)
        else:
            target = best_r
    else:
        target = (w // 2, h // 2)

    tx, ty = target
    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Higher advantage, then smaller own distance, then prefer moves that also reduce board-bounds issues deterministically.
        adv = do - ds2
        key = (-adv, ds2, nx, ny)
        if best_key is None or key < best_key:
            best_key, best_move = key, (dx, dy)

    return [best_move[0], best_move[1]]