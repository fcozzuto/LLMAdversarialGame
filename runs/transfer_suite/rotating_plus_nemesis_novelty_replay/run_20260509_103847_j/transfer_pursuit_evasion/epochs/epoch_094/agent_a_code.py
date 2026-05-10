def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("escap" in role) or ("run" in role) or ("runner" in role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x, y):
        ax = abs(x - ox)
        ay = abs(y - oy)
        return ax if ax > ay else ay

    obs_list = list(blocked)

    def nearest_obstacle_dist(x, y):
        if not obs_list:
            return 99
        best = 99
        for bx, by in obs_list:
            d = abs(x - bx) + abs(y - by)
            if d < best:
                best = d
        return best

    # If capture radius is 0, exact capture occurs on same cell; avoid only when evader.
    best = (None, None, None)
    if is_evader:
        best_val = (-10**9, -10**9, -10**9)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny)
            if (nx == ox and ny == oy) and int(observation.get("capture_radius") or 0) == 0:
                continue
            nd = nearest_obstacle_dist(nx, ny)
            # Primary: maximize distance; secondary: stay far from obstacles; tertiary: prefer board corners deterministically.
            corner_bonus = max(nx, w - 1 - nx) + max(ny, h - 1 - ny)
            val = (d, nd, corner_bonus)
            if val > best_val:
                best_val = val
                best = (dx, dy, val)
        if best[0] is not None:
            return [int(best[0]), int(best[1])]
    else:
        best_val = (10**9, -10**9, 10**9)
        center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny)
            # Primary: minimize distance; secondary: prefer moving "towards" center (more deterministic); tertiary: prefer larger clearance.
            cx = abs(nx - center_x)
            cy = abs(ny - center_y)
            clearance = nearest_obstacle_dist(nx, ny)
            val = (d, -(cx + cy), -clearance)
            if val < best_val:
                best_val = val
                best = (dx, dy, val)
        if best[0] is not None:
            return [int(best[0]), int(best[1])]

    return [0, 0]