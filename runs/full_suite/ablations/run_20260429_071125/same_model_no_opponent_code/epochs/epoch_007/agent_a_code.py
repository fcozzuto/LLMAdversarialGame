def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {tuple(p) for p in observation.get("obstacles", [])}
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def safe(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def free_neighbors(nx, ny):
        c = 0
        for dx, dy in deltas:
            tx, ty = nx + dx, ny + dy
            if safe(tx, ty):
                c += 1
        return c

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_val = -10**30
    best = (0, 0)
    if not resources:
        dirs = deltas
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if safe(nx, ny):
                val = -cheb(nx, ny, cx, cy) - 2 * cheb(nx, ny, ox, oy) + free_neighbors(nx, ny)
                if val > best_val:
                    best_val = val
                    best = (dx, dy)
        return [best[0], best[1]]

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not safe(nx, ny):
            continue

        my_best = 10**9
        val = 0
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            my_best = myd if myd < my_best else my_best
            diff = opd - myd  # positive if we are closer (or tie)
            if diff >= 0:
                val += diff * 8 + 20 - myd
            else:
                val += diff * 4  # being farther is bad

        val += 12 - my_best
        val += free_neighbors(nx, ny) * 2
        val -= cheb(nx, ny, ox, oy) // 2  # keep pressure/control spacing
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]]