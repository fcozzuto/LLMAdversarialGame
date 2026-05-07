def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turns_remaining = observation.get("turns_remaining", 0)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return max(abs(x2 - x1), abs(y2 - y1))

    dirs = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    res_list = [tuple(r) for r in resources]

    if not res_list:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    best_move = (0, 0)
    best_key = None  # higher is better

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        best_for_this_move = None
        for rx, ry in res_list:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            adv = od - sd  # >0 means we arrive earlier under this metric
            # Prefer moves that can beat opponent; if not, still head to something closer to us
            # and slightly deprioritize very late pickups (when turns_remaining is small).
            lateness_pen = 0
            if turns_remaining:
                lateness_pen = max(0, sd - turns_remaining) * 0.01
            # Key tuple: (beat_amount, -sd, -od) to make better earlier pickups win deterministically
            key = (adv - lateness_pen, -sd, -od)
            if best_for_this_move is None or key > best_for_this_move:
                best_for_this_move = key

        if best_for_this_move is None:
            continue
        if best_key is None or best_for_this_move > best_key:
            best_key = best_for_this_move
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]