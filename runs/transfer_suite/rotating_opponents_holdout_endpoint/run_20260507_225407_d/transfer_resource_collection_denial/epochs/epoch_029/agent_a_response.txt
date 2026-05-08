def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick resource that is most "ours" under a go-first race heuristic.
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        sd = dist_cheb(sx, sy, rx, ry)
        od = dist_cheb(ox, oy, rx, ry)
        # Prefer resources where opponent is farther (positive advantage).
        key = (od - sd, -sd)  # larger advantage; then smaller sd
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        # No visible resources: drift to center while avoiding obstacles.
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Avoid stepping next to obstacles.
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obs:
                    adj_pen += 1
        # Move toward target; also discourage moves that give opponent a shortcut (race term).
        myd = dist_cheb(nx, ny, tx, ty)
        opd = dist_cheb(ox, oy, tx, ty)
        val = (-(myd), (opd - myd), -adj_pen)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]