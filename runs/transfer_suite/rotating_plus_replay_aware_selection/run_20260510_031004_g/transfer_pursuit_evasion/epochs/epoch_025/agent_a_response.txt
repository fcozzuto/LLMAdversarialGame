def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role", "") or "").lower()
    evader = ("evader" in role) or ("runner" in role)

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    target_corner = min(corners, key=lambda c: dist2((ox, oy), c))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue

        d_opp = dist2((nx, ny), (ox, oy))
        d_corner = dist2((nx, ny), target_corner)
        d_opp_from = dist2((sx, sy), (ox, oy))
        corner_move = dist2((nx, ny), target_corner) - dist2((sx, sy), target_corner)

        if evader:
            score = d_opp + 0.9 * (-d_corner) + 0.05 * corner_move
            better = (best_score is None) or (score > best_score)
        else:
            score = -d_opp + 0.35 * (-d_corner) + 0.05 * (-corner_move)
            better = (best_score is None) or (score > best_score)

        if better:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]