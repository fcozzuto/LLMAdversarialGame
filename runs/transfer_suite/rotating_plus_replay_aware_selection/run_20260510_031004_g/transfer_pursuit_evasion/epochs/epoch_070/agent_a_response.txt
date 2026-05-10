def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    if "purs" in self_role:
        is_pursuer = True
    elif "evad" in self_role:
        is_pursuer = False
    else:
        is_pursuer = ("evad" in opp_role) is False

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def nearest_obst_d2(x, y):
        if not obstacles:
            return 10**9
        best = 10**18
        for bx, by in obstacles:
            d = (x - bx) * (x - bx) + (y - by) * (y - by)
            if d < best:
                best = d
        return best if best != 10**18 else 10**9

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            nx, ny = sx, sy
        blocked = (nx, ny) in obstacles
        d_op = dist2(nx, ny, ox, oy)
        d_obs = nearest_obst_d2(nx, ny)
        toward = dist2(nx, ny, far_corner[0], far_corner[1]) if not is_pursuer else dist2(nx, ny, near_corner[0], near_corner[1])

        if is_pursuer:
            # Minimize distance to opponent; strongly avoid obstacles; slightly prefer moving toward "near" corner.
            score = d_op * 10 + (0 if not blocked else 10**10) + (10**6 / max(1, d_obs)) + toward * 0.01
            better = best_score is None or score < best_score
        else:
            # Maximize distance to opponent; avoid obstacles; slightly prefer far corner.
            score = -d_op * 10 + (0 if not blocked else 10**10) + (10**6 / max(1, d_obs)) + toward * 0.01
            better = best_score is None or score < best_score  # since score is lower-is-better here
        if better:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]