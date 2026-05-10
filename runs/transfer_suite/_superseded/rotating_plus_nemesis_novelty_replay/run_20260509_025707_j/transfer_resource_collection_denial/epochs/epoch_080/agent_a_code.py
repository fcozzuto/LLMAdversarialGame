def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def greedy_step(px, py, tx, ty):
        dx = 0 if tx == px else (1 if tx > px else -1)
        dy = 0 if ty == py else (1 if ty > py else -1)
        nx, ny = px + dx, py + dy
        if ok(nx, ny):
            return nx, ny
        if ok(px + dx, py):
            return px + dx, py
        if ok(px, py + dy):
            return px, py + dy
        if ok(px, py):
            return px, py
        # deterministic fallback: first valid neighbor in dirs order
        for ddx, ddy in dirs:
            nx, ny = px + ddx, py + ddy
            if ok(nx, ny):
                return nx, ny
        return px, py

    # Predict opponent's next target using greedy nearest-resource (tie-break by coords)
    best_t = None
    best_d = None
    for r in resources:
        rx, ry = r[0], r[1]
        d = dist(ox, oy, rx, ry)
        key = (d, rx, ry)
        if best_d is None or key < best_d:
            best_d = key
            best_t = (rx, ry)
    opp_nx, opp_ny = greedy_step(ox, oy, best_t[0], best_t[1])

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        gap_best = -10**18
        gap_sum = 0
        win_bonus = 0
        for r in resources:
            rx, ry = r[0], r[1]
            my_d = dist(nx, ny, rx, ry)
            opp_d = dist(opp_nx, opp_ny, rx, ry)
            gap = opp_d - my_d
            if gap > gap_best:
                gap_best = gap
            if gap > 0:
                gap_sum += gap
            if my_d == 0:
                win_bonus += 1000
        val = 10 * gap_best + gap_sum + win_bonus
        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move