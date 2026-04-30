def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_obs(x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in obstacles:
                c += 1
        return c

    def best_resource_value(px, py):
        if not resources:
            tx, ty = w // 2, h // 2
            return -cheb(px, py, tx, ty) - 0.25 * adj_obs(px, py)
        bestv = -10**18
        for rx, ry in resources:
            d_me = cheb(px, py, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            v = (d_op - d_me) * 10.0 - d_me * 0.2 - adj_obs(rx, ry) * 1.0
            # Prefer resources that are not "ahead" of opponent
            if d_me <= d_op:
                v += 5.0
            else:
                v -= 2.0
            if v > bestv:
                bestv = v
        return bestv

    best = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        v = best_resource_value(nx, ny)
        # Slightly prefer staying closer to center to reduce corner traps
        cx, cy = w // 2, h // 2
        v -= 0.03 * cheb(nx, ny, cx, cy)
        # Avoid moving into tight obstacle proximity
        v -= 0.15 * adj_obs(nx, ny)
        if v > best:
            best = v
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]