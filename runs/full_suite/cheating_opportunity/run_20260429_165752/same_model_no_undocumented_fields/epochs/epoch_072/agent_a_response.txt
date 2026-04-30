def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            cand.append((dx, dy))
    if not cand:
        return [0, 0]

    if not resources:
        best = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            # drift away from opponent a bit
            val = cheb(nx, ny, ox, oy)
            key = (-val, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1]

    best_key = None
    best_move = [0, 0]
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        # choose resource where we are not too far behind the opponent
        best_target = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # penalty if opponent is much closer; reward if we're competitive
            behind = opd - myd
            target_val = myd + (2.0 * behind if behind > 0 else 0.0) + (0.15 * cheb(nx, ny, rx, ry) + 0.05 * (rx + ry))
            if best_target is None or target_val < best_target:
                best_target = target_val
        # prefer moves that reduce distance from current best targeting
        # (small tie-breakers: progress, then deterministic order)
        progress = cheb(sx, sy, ox, oy) - cheb(nx, ny, ox, oy)
        move_cost = best_target - 0.02 * progress + (0.001 if dx == 0 and dy == 0 else 0.0)
        key = (move_cost, abs(dx), abs(dy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move