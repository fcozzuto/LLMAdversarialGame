def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    def adj_obs(x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in obstacles:
                c += 1
        return c

    if resources:
        best_t = None
        best_v = -10**18
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            v = (d_op - d_me) * 10.0 - d_me * 0.7 - adj_obs(rx, ry) * 1.6 + (cheb(rx, ry, w//2, h//2) * -0.02)
            if v > best_v:
                best_v = v
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        tx, ty = w // 2, h // 2

    # Evaluate moves: free cells; prefer closer to target and farther from opponent.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_to = cheb(nx, ny, tx, ty)
        d_op = cheb(nx, ny, ox, oy)
        # Small preference for moving along gradient and avoiding being boxed in.
        val = -d_to * 3.0 + d_op * 1.2 - adj_obs(nx, ny) * 0.9
        # Deterministic tie-break: lexicographic on (dx, dy) by using current order.
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]