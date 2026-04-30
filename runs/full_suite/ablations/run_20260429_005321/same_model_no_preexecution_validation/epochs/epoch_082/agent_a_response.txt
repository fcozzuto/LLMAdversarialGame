def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cell_ok(x, y): return inb(x, y) and (x, y) not in obstacles

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

    tx, ty = (w // 2, h // 2)
    if resources:
        best = resources[0]
        bestv = -10**18
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer where we are closer than opponent; also prefer closer overall; penalize obstacle-heavy cells.
            v = (d_op - d_me) * 9 - d_me * 0.9 - adj_obs(rx, ry) * 1.2
            # Slightly favor resources on our “side” (closer to us than mid) to avoid random chasing.
            v += -0.15 * cheb(rx, ry, w // 2, h // 2)
            if v > bestv:
                bestv = v
                best = (rx, ry)
        tx, ty = best

    # If opponent is extremely close to the same target, shift to a different resource deterministically.
    if resources:
        d_me = cheb(sx, sy, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        if d_op + 1 < d_me:
            best = None
            bestv = -10**18
            for rx, ry in resources:
                d_me2 = cheb(sx, sy, rx, ry)
                d_op2 = cheb(ox, oy, rx, ry)
                v = (d_op2 - d_me2) * 10 - d_me2 - adj_obs(rx, ry) * 1.3
                if v > bestv:
                    bestv = v
                    best = (rx, ry)
            if best is not None:
                tx, ty = best

    # Choose move that best reduces distance to target, with tie-breaks for obstacle avoidance and not letting opponent gain.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        my_d = cheb(nx, ny, tx, ty)
        op_d = cheb(ox, oy, tx, ty)
        step_gain = (cheb(sx, sy, tx, ty) - my_d)
        # Reward closing in; penalize getting stuck near obstacles; small penalty if opponent is already far ahead to that target.
        val = step_gain * 4.0 - my_d * 0.2 - adj_obs(nx, ny) * 0.7
        if resources:
            val += (op_d - my_d) * 0.25
        # Prefer staying still slightly only when surrounded by obstacles.
        if dx == 0 and dy == 0:
            val -= adj_obs(sx, sy) * 0.05
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]