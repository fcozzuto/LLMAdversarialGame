def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def center(x, y):
        cx, cy = w // 2, h // 2
        return cheb(x, y, cx, cy)

    def obstacle_prox(x, y):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    c += 1
        return c

    best_move = (0, 0)
    best_val = -10**18
    valid_any = False

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        valid_any = True

        if resources:
            best_res_val = -10**18
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Prefer resources where we can be earlier; penalize if opponent is likely to take soon.
                adv = do - ds
                soon_threat = 6 if do <= ds + 1 else 0
                block = obstacle_prox(rx, ry) + 0.5 * obstacle_prox(nx, ny)
                # Mild anti-tie: prefer slightly closer to center to keep options.
                v = adv * 12 - soon_threat - block - 0.3 * center(nx, ny)
                if v > best_res_val:
                    best_res_val = v
            val = best_res_val
        else:
            val = -center(nx, ny) - 0.2 * obstacle_prox(nx, ny)

        # Deterministic tie-break: prefer staying, then smaller dx, then smaller dy.
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            if (dx, dy) == (0, 0):
                best_move = (dx, dy)
            elif best_move != (0, 0) and (dx, dy) < best_move:
                best_move = (dx, dy)

    if not valid_any:
        return [0, 0]
    return [best_move[0], best_move[1]]