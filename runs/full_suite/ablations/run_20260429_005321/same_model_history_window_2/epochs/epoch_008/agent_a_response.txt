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

    def obs_near(x, y):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    c += 1
        return c

    cx, cy = w // 2, h // 2
    valid_res = [(rx, ry) for (rx, ry) in resources if (rx, ry) not in obstacles]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        center_bias = -0.05 * cheb(nx, ny, cx, cy)
        wall_bias = -0.25 * obs_near(nx, ny)

        if not valid_res:
            val = center_bias + wall_bias
        else:
            # Focus on the best few resources deterministically
            # (sorted by distance from our current position)
            res_sorted = sorted(valid_res, key=lambda r: cheb(sx, sy, r[0], r[1]))
            top = res_sorted[:5]
            val = center_bias + wall_bias
            for rx, ry in top:
                d_self = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                # Prefer resources we reach sooner than opponent
                # Extra weight for immediate capture
                capture = 2.0 if d_self == 0 else 0.0
                reach_adv = (d_opp - d_self)
                val += 1.15 * reach_adv + capture

            # Mildly discourage moving away from overall closest target
            cur_best = min(cheb(sx, sy, rx, ry) for (rx, ry) in valid_res)
            nxt_best = min(cheb(nx, ny, rx, ry) for (rx, ry) in valid_res)
            val += 0.08 * (cur_best - nxt_best)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]