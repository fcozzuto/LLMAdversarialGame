def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

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

    neigh_dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def obst_adj_pen(x, y):
        pen = 0
        for dx, dy in neigh_dirs:
            if (x + dx, y + dy) in obst:
                pen += 1
        return pen

    # If no resources, just avoid obstacles and keep some distance from opponent.
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = -10**18
    opp_dist_now = cheb(sx, sy, ox, oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst:
            continue

        # Resource shaping: move to reduce distance to the best available resource,
        # with a small preference for being closer than opponent.
        if resources:
            best_res_val = -10**18
            for rx, ry in resources:
                d_self = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                # If we can reach it significantly sooner, value spikes.
                rel = d_opp - d_self
                # Prefer closer resources even if opponent is also near.
                val = 40 * rel - d_self
                best_res_val = val if val > best_res_val else best_res_val
        else:
            best_res_val = 0

        # Obstacle proximity penalty and general safety.
        pen = obst_adj_pen(nx, ny)
        # Opponent avoidance: if too close, strongly move away; otherwise keep neutral.
        opp_dist = cheb(nx, ny, ox, oy)
        avoid = 0
        if opp_dist_now <= 2 or opp_dist <= 2:
            avoid = 15 * (opp_dist - opp_dist_now) - 8 * (2 - opp_dist if opp_dist < 2 else 0)
        else:
            avoid = 2 * (opp_dist - opp_dist_now)

        # Mild center bias to reduce cornering traps.
        cx, cy = w // 2, h // 2
        center = -0.5 * cheb(nx, ny, cx, cy)

        v = best_res_val - 5 * pen + avoid + center
        if v > best_val:
            best_val = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]