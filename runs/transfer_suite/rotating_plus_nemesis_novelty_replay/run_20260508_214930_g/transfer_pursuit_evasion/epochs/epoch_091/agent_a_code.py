def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = (observation.get("self_role", "") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "fugitive"))
    is_pursuer = any(k in role for k in ("pursuer", "hunter", "seeker"))
    if not is_evader and not is_pursuer:
        is_pursuer = True

    obstacles = observation.get("obstacles") or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    deltas.sort(key=lambda d: (d[0], d[1]))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    nearest_obs_dist = lambda x, y: (min((abs(x - bx) + abs(y - by) for (bx, by) in obs), default=99) if obs else 99)

    target_corner = None
    if is_evader:
        best_corner_val = None
        for cx, cy in corners:
            corner_val = (abs(cx - ox) + abs(cy - oy))
            if obs:
                corner_val += 0.02 * min(abs(cx - bx) + abs(cy - by) for (bx, by) in obs)
            if best_corner_val is None or corner_val > best_corner_val:
                best_corner_val, target_corner = corner_val, (cx, cy)
        tx, ty = target_corner
    else:
        tx, ty = ox, oy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        dist_op = abs(nx - ox) + abs(ny - oy)
        dist_obs = nearest_obs_dist(nx, ny)
        if is_pursuer:
            # primary: approach opponent; secondary: keep distance from obstacles
            score = (-dist_op) + 0.15 * dist_obs
            # slight preference for diagonal/axis moves that reduce Chebyshev quickly
            score += 0.01 * (max(abs(nx - ox), abs(ny - oy)) * -1)
        else:
            # evader_corner style: move away, while steering toward the chosen farthest corner
            dist_corner = abs(nx - tx) + abs(ny - ty)
            score = (dist_op) + 0.12 * dist_obs - 0.05 * dist_corner
            # avoid standing still if it doesn't improve safety
            if dx == 0 and dy == 0:
                score -= 0.02

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move