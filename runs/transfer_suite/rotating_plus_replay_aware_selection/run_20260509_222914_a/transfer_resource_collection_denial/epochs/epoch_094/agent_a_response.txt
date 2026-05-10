def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def dist_diag(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Focus on few closest resources to reduce noise and stay deterministic
    res_sorted = sorted(resources, key=lambda r: (dist_diag(sx, sy, r[0], r[1]), r[0], r[1]))
    res_consider = res_sorted[:min(5, len(res_sorted))]

    best_val = -10**18
    best_move = [0, 0]
    alpha = 1.15  # prioritize resources where we are closer than opponent

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy  # engine would keep us in place

        local_best = -10**18
        for rx, ry in res_consider:
            sd = dist_diag(nx, ny, rx, ry)
            od = dist_diag(ox, oy, rx, ry)
            # maximize advantage; slight penalty for moving "slow"
            val = (od - sd) * alpha - 0.08 * sd
            if val > local_best:
                local_best = val

        if local_best > best_val or (local_best == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = local_best
            best_move = [dx, dy]

    # If all are similar, bias toward reducing distance to the single best resource (deterministic tie-break)
    return best_move