def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs_set = set()
    for p in obstacles:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs_set.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return inb(x, y) and (x, y) not in obs_set

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If resources exist: prefer one where we are closer than opponent; else go to closest.
    def target_score(x, y, rx, ry):
        dm = cheb(x, y, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Higher is better.
        # If opponent is already closer, heavily penalize.
        lead = do - dm  # positive => we closer
        return (10.0 * lead) - (1.2 * dm) - (0.3 * cheb(rx, ry, sx, sy))

    def obstacle_pen(x, y):
        if not obs_set:
            return 0.0
        # Penalize being within 1 king-move of an obstacle; forbid stepping onto obstacle via legal().
        pen = 0.0
        for px, py in obs_set:
            d = cheb(x, y, px, py)
            if d == 0:
                return 1e9
            if d == 1:
                pen += 1.5
        return pen

    best_move = (0, 0)
    best_val = -1e18

    have_res = len(resources) > 0
    # Precompute resource list as int tuples.
    res_list = []
    for r in resources:
        if r is None or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs_set:
            res_list.append((rx, ry))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        val = -0.2 * cheb(nx, ny, ox, oy)  # avoid opponent
        val -= 0.35 * obstacle_pen(nx, ny)

        if have_res and res_list:
            # Choose best reachable direction toward a good resource.
            best_t = -1e18
            for rx, ry in res_list:
                # Small direction bias: don't go "through" occupied cells too long (cheap).
                t = target_score(nx, ny, rx, ry)
                # Encourage actual progress (closer to resource than from current pos)
                t += 0.9 * (cheb(sx, sy, rx, ry) - cheb(nx, ny, rx, ry))
                # If we can grab it immediately, spike.
                if nx == rx and ny == ry:
                    t += 25.0
                if t > best_t:
                    best_t = t
            val += best_t
        else:
            # No resources: move toward center while keeping distance from opponent.
            cx, cy = w // 2, h // 2
            val += 1.2 * (cheb(sx, sy, ox, oy) - cheb(nx, ny, ox, oy))
            val -= 0.9 * cheb(nx, ny, cx, cy)

        # Deterministic tie-break: prefer staying if equal? We'll prefer lexicographically smallest (dx,dy).
        if val > best_val + 1e-9:
            best_val = val
            best_move = (dx, dy)
        elif abs(val - best_val) <= 1e-9:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]