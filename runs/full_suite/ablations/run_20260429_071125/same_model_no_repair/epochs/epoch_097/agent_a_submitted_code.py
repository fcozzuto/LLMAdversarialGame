def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = [0, 0]
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles: 
                continue
            v = -cheb(nx, ny, cx, cy) - 0.01 * (dx * dx + dy * dy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    my_op_nearest = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my_nearest = None
        my_target = None
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if my_nearest is None or d < my_nearest or (d == my_nearest and (rx, ry) < my_target):
                my_nearest = d
                my_target = (rx, ry)

        tx, ty = my_target
        op_to_target = cheb(ox, oy, tx, ty)

        # Prefer being strictly closer than opponent to the same contested target.
        contest_pen = 6.0 if op_to_target <= my_nearest else 0.0

        # Slight preference to reduce opponent's reach overall.
        op_reach = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
        center_pen = 0.01 * ((nx - (w - 1) / 2.0) ** 2 + (ny - (h - 1) / 2.0) ** 2)

        val = (-1.7 * my