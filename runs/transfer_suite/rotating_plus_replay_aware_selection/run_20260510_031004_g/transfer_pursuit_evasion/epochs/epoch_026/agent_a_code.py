def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role", "") or "").lower()
    evader = ("evader" in role) or ("runner" in role) or ("escape" in role)
    pursuer = ("pursuer" in role) or ("chaser" in role)

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

    target_corner = max(corners, key=lambda c: dist2((ox, oy), c))
    if pursuer and not evader:
        target_corner = (ox, oy)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue

        d_to_opp = dist2((nx, ny), (ox, oy))
        if evader and not pursuer:
            d_corner = dist2((nx, ny), target_corner)
            val = (d_to_opp, d_corner)
        else:
            d_corner = dist2((nx, ny), target_corner)
            val = (-d_to_opp, -d_corner)

        if best is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]