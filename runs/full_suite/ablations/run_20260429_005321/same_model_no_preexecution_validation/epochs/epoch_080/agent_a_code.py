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
    def neigh_obs(x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in obstacles: c += 1
        return c
    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = resources[0]; bestv = -10**18
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            v = (d_op - d_me) * 100 - d_me - 0.5 * neigh_obs(rx, ry)
            # deterministic tie-breaker
            if v > bestv or (v == bestv and (rx, ry) < best):
                bestv = v; best = (rx, ry)
        tx, ty = best
    best_move = (0, 0); best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles: continue
        d_me = cheb(nx, ny, tx, ty)
        # Move that also tends to "delay" opponent: maximize opponent's relative distance to same target
        d_op = cheb(ox, oy, tx, ty)
        # Small preference to approach target and avoid getting boxed
        sc = (d_op - d_me) * 50 - d_me - 2.0 * neigh_obs(nx, ny)
        # Encourage not wandering: slight pull toward opponent direction midpoint (consistent contest for center)
        mx, my = (tx + ox) // 2, (ty + oy) // 2
        sc += 0.03 * cheb(nx, ny, mx, my) * -1
        if sc > best_sc or (sc == best_sc and (dx, dy) < best_move):
            best_sc = sc; best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]