def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = w // 2, h // 2

    if not inb(sx, sy) or w <= 0 or h <= 0:
        return [0, 0]

    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if resources:
            best_res_val = None
            for rx, ry in resources:
                ds = dist((nx, ny), (rx, ry))
                do = dist((ox, oy), (rx, ry))
                adv = do - ds  # positive means we are closer
                # discourage giving opponent an immediate grab when we're not better
                immediate_pen = -20 if do <= 1 and adv < 0 else 0
                # reward taking closer resources; slight center bias to avoid edge traps
                center_bias = -0.01 * (abs(rx - cx) + abs(ry - cy))
                res_val = adv * 10 - ds + center_bias + immediate_pen
                if best_res_val is None or res_val > best_res_val:
                    best_res_val = res_val
            # also avoid moves that reduce freedom near obstacles
            block_pen = 0
            for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ax, ay = nx + adx, ny + ady
                if not inb(ax, ay) or (ax, ay) in obstacles:
                    block_pen += 1
            val = best_res_val - 2.0 * block_pen
        else:
            # no resources: move toward center while maximizing distance from opponent
            dcenter = abs(nx - cx) + abs(ny - cy)
            dopp = dist((nx, ny), (ox, oy))
            val = dcenter * -1 + dopp * 0.5 - 2.0 * (0 if (nx, ny) not in obstacles else 1)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]