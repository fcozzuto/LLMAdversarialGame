def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = [(int(x), int(y)) for x, y in (observation.get("resources") or [])]
    obstacles = {(int(x), int(y)) for x, y in (observation.get("obstacles") or [])}
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    def near_obs(x, y):
        c = 0
        for ddx, ddy in dirs:
            if (x + ddx, y + ddy) in obstacles:
                c += 1
        return c

    cx, cy = (w - 1) // 2, (h - 1) // 2
    tx, ty = cx, cy
    best_target_val = -10**18

    # Pick a target resource deterministically; prefer those we can reach earlier.
    if resources:
        for rx, ry in resources:
            d1 = cheb(sx, sy, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            # If we are closer than opponent, strongly prefer; otherwise still pick if near.
            lead = d2 - d1
            v = 3.0 * lead - 0.6 * d1 - 0.15 * near_obs(rx, ry)
            if v > best_target_val:
                best_target_val = v
                tx, ty = rx, ry
    else:
        tx, ty = cx, cy

    # Move selection: greedily reduce distance to target, avoid obstacles, and block if possible.
    bestm = (0, 0); bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_me = cheb(nx, ny, tx, ty)
        d_op = cheb(nx, ny, ox, oy)
        # Encourage approaching target and keeping some distance from opponent.
        # Also discourage stepping into tight obstacle neighborhoods.
        v = -1.2 * d_me - 0.25 * near_obs(nx, ny) + 0.12 * d_op
        # Competitive tweak: if we can be the first to target, reward that more.
        if resources:
            dt_me = cheb(nx, ny, tx, ty)
            dt_op = cheb(ox, oy, tx, ty)
            v += 2.0 * (dt_op - dt_me)
        if v > bestv:
            bestv = v
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]