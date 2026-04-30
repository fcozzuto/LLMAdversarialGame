def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def adj_obs(x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in obstacles: c += 1
        return c

    if not resources:
        tx, ty = w // 2, h // 2
        best = (-10**18, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): continue
            v = -cheb(nx, ny, tx, ty) - 0.25 * adj_obs(nx, ny)
            if v > best[0]: best = (v, dx, dy)
        return [best[1], best[2]]

    # Score candidate next moves by best achievable "advantage" to any resource.
    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): continue
        worst = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            if d_me == 0: v = 10**9
            else:
                # Prefer resources where we are closer than opponent; penalize obstacle-adjacent cells.
                v = (d_op - d_me) * 20 - d_me * 2 - 0.6 * adj_obs(nx, ny)
            if v > worst: worst = v
        # Small tiebreaker: don't go to very obstacle-heavy cells.
        v2 = worst - 0.1 * adj_obs(nx, ny) - 0.01 * cheb(nx, ny, ox, oy)
        if v2 > best[0]: best = (v2, dx, dy)
    return [best[1], best[2]]