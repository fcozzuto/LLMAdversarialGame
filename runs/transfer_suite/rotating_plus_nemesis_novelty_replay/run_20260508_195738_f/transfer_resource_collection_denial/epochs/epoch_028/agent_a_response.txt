def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            v = man(ox, oy, cx, cy) - 0.01 * man(sx, sy, cx, cy)
            if best is None or v > best[0]:
                best = (v, cx, cy)
        tx, ty = best[1], best[2]
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [int(dx), int(dy)]

    res = [(int(r[0]), int(r[1])) for r in resources]
    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Prefer moves that make us win/lead on nearby resources; also slight tie-break by closeness to resources.
        val = 0.0
        for rx, ry in res:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            if sd == 0:
                val += 10000.0
                continue
            # Winning pressure: bigger when (od - sd) is larger; also prefer smaller sd.
            win = (od - sd)
            val += 50.0 * win - 0.5 * sd
        # Small obstacle pressure: discourage moving adjacent to obstacles
        for ax, ay in obstacles:
            if man(nx, ny, ax, ay) == 1:
                val -= 3.0
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]