def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            sc = man(ox, oy, cx, cy) * 2 - man(sx, sy, cx, cy)
            if best is None or sc > best[0]:
                best = (sc, cx, cy)
        tx, ty = best[1], best[2]
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [int(dx), int(dy)]

    cand_moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    res = [(int(r[0]), int(r[1])) for r in resources]

    best_move = (None, -10**18)
    for dx, dy in cand_moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        best_target_val = -10**18
        for rx, ry in res:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            takeover = 100 if sd <= od else 0
            val = (od - sd) * 50 + takeover - sd
            if val > best_target_val:
                best_target_val = val
        if best_target_val > best_move[1]:
            best_move = ((dx, dy), best_target_val)

    dx, dy = best_move[0]
    return [int(dx), int(dy)]