def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cell_ok(x, y): return inb(x, y) and (x, y) not in obstacles
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

    best_target = None
    best_score = -10**18
    if resources:
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Take targets where we are relatively closer; penalize being blocked near obstacles.
            v = (d_op - d_me) * 10 - d_me * 0.8 - adj_obs(rx, ry) * 1.5
            # Add a small tie-breaker to avoid always picking the first resource.
            v += -0.001 * (rx + 2 * ry)
            if v > best_score:
                best_score = v
                best_target = (rx, ry)

    # Candidate move selection with 1-step lookahead.
    best_move = (0, 0)
    best_move_v = -10**18
    cx, cy = (w // 2, h // 2)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        # If no target, drift to center while staying safe.
        if best_target is None:
            v = -cheb(nx, ny, cx, cy) - adj_obs(nx, ny) * 1.2
        else:
            rx, ry = best_target
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Also try to "shadow": don't step toward squares that let opponent gain dramatically.
            v = (d_op - d_me) * 12 - d_me * 0.9 - adj_obs(nx, ny) * 1.4
            # Micro-block: if we're adjacent to opponent, prefer moving away from it unless it helps the target.
            d_opp = cheb(nx, ny, ox, oy)
            v += (d_opp - 1) * 0.6
        if v > best_move_v:
            best_move_v = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]