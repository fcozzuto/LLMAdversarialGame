def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role_self = str(observation.get("self_role", "") or "").lower()
    self_is_evader = ("evader" in role_self) or ("runner" in role_self) or ("evasion" in role_self)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Prefer to break ties deterministically by move order, so keep fixed order.
    best_move = [0, 0]
    best_val = None

    # Corner bias: flee toward farthest corner; chase toward nearest corner.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def corner_bias(x, y):
        if self_is_evader:
            # maximize distance to nearest corner (i.e., generally head to a corner away from opponent)
            return max(abs(cx - x) + abs(cy - y) for cx, cy in corners)
        else:
            # minimize distance to nearest corner (generally restrict space)
            return -min(abs(cx - x) + abs(cy - y) for cx, cy in corners)

    adj_dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d = dist2(nx, ny, ox, oy)
        man = abs(nx - ox) + abs(ny - oy)

        # Obstacle proximity penalty to avoid getting boxed in.
        prox = 0
        for ax, ay in adj_dirs:
            if (nx + ax, ny + ay) in obstacles:
                prox += 1
        obstacle_pen = 10 * prox

        # Deterministic secondary: encourage moving that changes separation along both axes.
        sep = (abs((nx - ox)) + abs((ny - oy)))
        move_pref = -sep if self_is_evader else -sep  # same sign; only evaluated by comparison below

        cb = corner_bias(nx, ny)
        if self_is_evader:
            val = (d * 100 + man * 10 + cb * 3) - obstacle_pen + (nx * 0.001 + ny * 0.002)
        else:
            val = (-d * 100 - man * 10 + cb * 3) - obstacle_pen + (-(nx * 0.001 + ny * 0.002))

        if best_val is None:
            best_val = val
            best_move = [dxm, dym]
        else:
            if val > best_val:
                best_val = val
                best_move = [dxm, dym]

    return [int(best_move[0]), int(best_move[1])]