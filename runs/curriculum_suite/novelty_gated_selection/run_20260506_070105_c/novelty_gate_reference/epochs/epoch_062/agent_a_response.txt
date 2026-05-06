def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist_cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick resource where we have the biggest "tempo" advantage over opponent
    best = None
    best_score = -10**9
    for rx, ry in resources:
        ds = dist_cheb(sx, sy, rx, ry)
        do = dist_cheb(ox, oy, rx, ry)
        # prefer we arrive much sooner; also avoid extremely far targets
        score = (do - ds) * 100 - ds
        if score > best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best
    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Try moves that reduce distance to target while avoiding obstacles and staying away from opponent
    best_mv = [0, 0]
    best_val = 10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_to_t = dist_cheb(nx, ny, tx, ty)
        d_to_o = dist_cheb(nx, ny, ox, oy)
        # Penalty if we are too close to opponent (shadow-like pressure)
        val = d_to_t * 10 - min(d_to_o, 5) * 6
        # Extra penalty for moving adjacent to obstacles (avoid tight squeezes)
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                x2, y2 = nx + ax, ny + ay
                if (x2, y2) in obstacles:
                    adj_obs += 1
        val += adj_obs * 3
        if val < best_val:
            best_val = val
            best_mv = [dx, dy]

    return [int(best_mv[0]), int(best_mv[1])]