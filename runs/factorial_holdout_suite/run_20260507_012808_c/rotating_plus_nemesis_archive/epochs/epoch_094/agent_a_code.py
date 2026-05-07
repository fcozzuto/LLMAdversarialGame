def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        for dx, dy in [(-1, 0), (1, 0), (0, 1), (0, -1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    # If standing on a resource, stay to collect.
    if (sx, sy) in resources:
        return [0, 0]

    # Choose resource where we are more likely to reach first.
    best_cell = None
    best_key = None
    for cx, cy in resources:
        ds = dist((sx, sy), (cx, cy))
        do = dist((ox, oy), (cx, cy))
        # Prefer cells that are not "too close" to obstacles (soft safety).
        near_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (cx + ax, cy + ay) in obstacles:
                    near_obs += 1
        # Lower is better: prioritize smaller ds; penalize giving opponent a faster/marked reach.
        key = (ds - 0.7 * do) + 0.25 * near_obs + 0.01 * (cx + cy)
        if best_key is None or key < best_key:
            best_key = key
            best_cell = (cx, cy)

    cx, cy = best_cell
    dx = 0 if cx == sx else (1 if cx > sx else -1)
    dy = 0 if cy == sy else (1 if cy > sy else -1)

    # Among legal moves, pick the one that most reduces our distance to the target.
    candidates = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            if mx == 0 and my == 0:
                pass
            if abs(mx) > 1 or abs(my) > 1:
                continue
            nx, ny = sx + mx, sy + my
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                dnew = dist((nx, ny), (cx, cy))
                # Small deterrent if move drifts away from opponent too strongly is not needed; keep simple.
                candidates.append((dnew, mx, my))
    if not candidates:
        return [0, 0]
    candidates.sort()
    return [int(candidates[0][1]), int(candidates[0][2])]