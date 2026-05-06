def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    def best_resource_value(x, y):
        best = None
        for r in resources:
            sd = dist2((x, y), r)
            od = dist2((ox, oy), r)
            val = (od - sd, -sd)  # prefer resources far from opponent and close to self
            if best is None or val > best[0]:
                best = (val, r)
        return best[0][0], best[0][1], best[1]

    # Prefer moves that improve the "best resource contest value" from the new position.
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        v1, v2, r = best_resource_value(nx, ny)
        # Secondary tie-break: move toward the chosen resource to prevent dithering
        step_goal = (r[0] - nx, r[1] - ny)
        tie = -abs(step_goal[0]) - abs(step_goal[1])
        val = (v1, v2, tie)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move