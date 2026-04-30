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
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy if False else (abs(dx) if abs(dx) > abs(dy) else abs(dy))

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Pick contested target: minimize (our_dist - opp_dist) then our_dist
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            ad = cheb(sx, sy, rx, ry)
            bd = cheb(ox, oy, rx, ry)
            key = (ad - bd, ad, -dist2(sx, sy, ox, oy))
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        # No resources visible: move toward center while keeping away from opponent
        tx, ty = w // 2, h // 2

    # Evaluate each possible move
    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Primary: reduce distance to target
        d_to = cheb(nx, ny, tx, ty)
        d2_to = dist2(nx, ny, tx, ty)

        # Secondary: avoid getting closer to opponent (contest/escape)
        opp_d = cheb(nx, ny, ox, oy)
        opp_pen = -opp_d  # prefer larger opp_d

        # Obstacle proximity penalty (local)
        obs_pen = 0
        for ax, ay in obstacles:
            if dist2(nx, ny, ax, ay) <= 1:
                obs_pen += 4
            elif dist2(nx, ny, ax, ay) <= 4:
                obs_pen += 1

        # Mild preference to move (prefer non-stay if equal)
        stay_pen = 1 if dx == 0 and dy == 0 else 0

        val = (d_to, d2_to, opp_pen, obs_pen, stay_pen)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move