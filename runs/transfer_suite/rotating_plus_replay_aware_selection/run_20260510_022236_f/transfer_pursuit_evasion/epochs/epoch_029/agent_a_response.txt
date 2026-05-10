def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) and ("purs" not in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # neighbor openness (avoid trapped steps deterministically)
        open_cnt = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if ok(tx, ty):
                open_cnt += 1

        my_to_opp = dist2(nx, ny, ox, oy)
        if is_evader:
            # prefer increasing distance and heading to far corner; penalize low mobility
            heading = dist2(nx, ny, far_corner[0], far_corner[1])
            score = my_to_opp * 5 - heading * 0.6 + open_cnt * 0.8
            # small tie-break: deterministic preference for moves with larger dx, then dy
            score = score + (dx * 0.01) + (dy * 0.001)
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)
        else:
            # pursuer: minimize distance; also bias toward near_corner to limit evader options
            heading = dist2(near_corner[0], near_corner[1], nx, ny)
            score = -my_to_opp * 5 - heading * 0.2 + open_cnt * 0.1
            score = score - (dx * 0.01) - (dy * 0.001)
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)

    if best is None:
        # Should not happen; fallback to staying put
        return [0, 0]
    return [int(best[0]), int(best[1])]