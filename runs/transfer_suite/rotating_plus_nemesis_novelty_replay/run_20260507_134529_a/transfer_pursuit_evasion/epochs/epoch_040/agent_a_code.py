def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or ("evader" in opponent_role and "pursuer" not in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    target_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy) if is_evader else dist2(c[0], c[1], sx, sy))

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if is_evader:
            d_to_p = dist2(nx, ny, ox, oy)
            d_tcorner = dist2(nx, ny, target_corner[0], target_corner[1])
            d_after = d_to_p + 0.15 * d_tcorner
            score = d_after  # maximize
        else:
            d_to_p = dist2(nx, ny, ox, oy)
            d_tcorner = dist2(nx, ny, target_corner[0], target_corner[1])
            # Greedy intercept: prioritize closing gap, but also steer toward the predicted corner.
            score = 1.7 * d_to_p + 0.25 * d_tcorner  # minimize
        if best is None or (score > best_score if is_evader else score < best_score):
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]