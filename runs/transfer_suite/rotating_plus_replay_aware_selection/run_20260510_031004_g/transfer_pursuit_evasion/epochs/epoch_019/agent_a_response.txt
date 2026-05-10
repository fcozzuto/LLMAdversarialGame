def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = str(observation.get("self_role", "") or "").lower()
    evader = "evader" in self_role

    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def free_moves(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                c += 1
        return c

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    target_corner = best_corner if evader else (w - 1 - best_corner[0], h - 1 - best_corner[1])

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs_set:
            continue
        if evader:
            # Keep maximizing distance; bias toward opposite corner and open space to resist zigzag capture.
            score = (dist2(nx, ny), free_moves(nx, ny), abs(nx - target_corner[0]) + abs(ny - target_corner[1]))
            if best_score is None or score > best_score:
                best_score, best = score, (dx, dy)
        else:
            # Pursuer: greedily reduce distance; use mobility and move toward the evader's side.
            score = (-dist2(nx, ny), free_moves(nx, ny), -abs(nx - target_corner[0]) - abs(ny - target_corner[1]))
            if best_score is None or score > best_score:
                best_score, best = score, (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]