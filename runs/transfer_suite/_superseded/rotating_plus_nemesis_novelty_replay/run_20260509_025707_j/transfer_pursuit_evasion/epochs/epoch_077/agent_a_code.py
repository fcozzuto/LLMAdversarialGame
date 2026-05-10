def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    i_am_evader = ("evader" in role) or ("runner" in role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles_list = list(obstacles)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def nearest_obstacle_dist2(x, y):
        if not obstacles_list:
            return 999999
        best = 999999
        for (ax, ay) in obstacles_list:
            d = dist2(x, y, ax, ay)
            if d < best:
                best = d
        return best

    # Wall preference for evader: try to move toward a far corner but keep close to a wall when possible.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy) if i_am_evader else dist2(c[0], c[1], sx, sy))
    target_x, target_y = far_corner

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_op = dist2(nx, ny, ox, oy)
        d_wall = min(nx, w - 1 - nx, ny, h - 1 - ny)  # 0 means on edge
        d_obs = nearest_obstacle_dist2(nx, ny)

        if i_am_evader:
            # Maximize distance from pursuer; prefer staying near walls (runner) unless blocked; avoid obstacles.
            score = (d_op, -d_wall, d_obs)
        else:
            # Pursuer: minimize distance to evader; prefer routes that are not too close to obstacles.
            score = (-d_op, d_wall, d_obs)

        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]

    return [int(best[1]), int(best[2])]