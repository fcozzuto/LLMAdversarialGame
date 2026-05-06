def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        # Deterministic drift toward opponent
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        if inside(sx + dx, sy + dy):
            return [dx, dy]
        return [0, 0]

    # Pick resource I'm likely to secure first
    best_r = None
    best_key = None
    for rx, ry in resources:
        my_d = dist(sx, sy, rx, ry)
        op_d = dist(ox, oy, rx, ry)
        # Prefer resources I can reach sooner; tie-break by smaller my_d, then farther from opponent
        key = (1 if my_d < op_d else 0, -(op_d - my_d), -my_d)
        # We want: (reach-priority, advantage, proximity), so reverse sign where needed
        # Convert to minimization:
        min_key = (-key[0], key[1], my_d, -op_d, rx, ry)
        if best_key is None or min_key < best_key:
            best_key = min_key
            best_r = (rx, ry)

    rx, ry = best_r
    # Evaluate one-step moves toward target; tie-break by maximizing distance from opponent
    cur_my = dist(sx, sy, rx, ry)
    cur_op = dist(ox, oy, sx, sy)
    best_m = None
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        my_d = dist(nx, ny, rx, ry)
        op_d = dist(nx, ny, ox, oy)
        # primary: decrease my distance; secondary: keep away from opponent; tertiary: avoid moving away from target
        val = ((cur_my - my_d), op_d, -(my_d), dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]