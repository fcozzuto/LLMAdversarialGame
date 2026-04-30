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
    def min_dist_to_obst(x, y):
        best = 10**9
        for ex, ey in obstacles:
            d = cheb(x, y, ex, ey)
            if d < best: best = d
        return best if obstacles else 10**9
    if not resources:
        tx, ty = w // 2, h // 2
    else:
        # Predict opponent's most likely target (different from pure "best cell" chasing)
        op_best = None
        op_cost = 10**18
        for rx, ry in resources:
            c = cheb(ox, oy, rx, ry) + 0.25 * adj_obs(rx, ry)
            if c < op_cost:
                op_cost = c
                op_best = (rx, ry)
        tx, ty = op_best if op_best is not None else (w // 2, h // 2)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Interception-oriented: either race any resource where we can be earlier,
        # otherwise specifically deny the predicted opponent target.
        if resources:
            my_adv = -10**18
            for rx, ry in resources:
                d_me = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                margin = d_op - d_me
                v = margin * 10.0 - d_me * 0.45 - 0.9 * adj_obs(rx, ry)
                if margin > 0:
                    v += 6.0  # encourage taking winning-at-arrival opportunities
                if v > my_adv: my_adv = v
            # Deny opponent's predicted focus if no immediate win
            deny = (cheb(nx, ny, tx, ty) - cheb(ox, oy, tx, ty)) * 6.0
        else:
            my_adv = 0
            deny = (cheb(nx, ny, tx, ty) - cheb(ox, oy, tx, ty)) * 6.0
        # Obstacle safety