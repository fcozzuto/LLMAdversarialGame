def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = (ox + sx) // 2, (oy + sy) // 2
        best = None
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                d = man(nx, ny, tx, ty)
                v = -d
                if v > bestv:
                    bestv = v
                    best = (dx, dy)
        return [best[0], best[1]]

    # Prefer moves that increase (opponent_distance - our_distance) to a contested resource
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Simple obstacle penalty to avoid tight corridors
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if 0 <= px < w and 0 <= py < h and (px, py) in obstacles:
                    adj_obs += 1

        best_res_score = -10**18
        best_res_dist = 10**18
        for rx, ry in resources:
            d_our = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            # Positive means we are closer than opponent to that resource
            score = (d_opp - d_our) * 10 - d_our
            # Prefer breaking ties toward our advantage
            if score > best_res_score or (score == best_res_score and d_our < best_res_dist):
                best_res_score = score
                best_res_dist = d_our

        # Small lure toward improving our position even if not fully contested
        towards_opponent = -man(nx, ny, ox, oy) * 0.01
        val = best_res_score - adj_obs * 2 + towards_opponent
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]