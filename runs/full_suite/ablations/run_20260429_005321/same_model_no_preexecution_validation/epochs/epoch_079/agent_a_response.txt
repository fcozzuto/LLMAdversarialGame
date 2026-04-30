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
    def obs_adj(x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in obstacles:
                c += 1
        return c

    if not resources:
        tx, ty = (w // 2, h // 2)
    else:
        # Choose a target where we are relatively closer than opponent (deterministic tie-break by ordering)
        best = resources[0]; bestv = -10**18
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # small bias toward nearer absolute progress and away from clutter
            v = (d_op - d_me) * 10 - d_me - 0.3 * obs_adj(rx, ry)
            if v > bestv:
                bestv = v; best = (rx, ry)
        tx, ty = best

    # One-step lookahead: pick move that improves our distance and advantage, avoiding obstacles
    best_move = (0, 0); best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_me = cheb(nx, ny, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        # Our relative advantage after move; penalize getting near obstacles more than opponent (reduces trap risk)
        score = (d_op - d_me) * 12 - d_me - 1.2 * obs_adj(nx, ny) + 0.1 * cheb(nx, ny, ox, oy)
        # Deterministic tie-break: prefer lower dx, then lower dy
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score; best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]