def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res_list = observation.get("resources") or []
    resources = []
    for r in res_list:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))

    def manhattan(a, b, c, d):
        x = a - c
        if x < 0:
            x = -x
        y = b - d
        if y < 0:
            y = -y
        return x + y

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            key = (manhattan(nx, ny, cx, cy), abs(nx - ox) + abs(ny - oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    # Contest heuristic: prefer moves that make us closer than opponent to some resource
    best_key = None
    best_move = (0, 0)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        self_best = 10**9
        diff_best = 10**9
        opp_best = 10**9
        for rx, ry in resources:
            dself = manhattan(nx, ny, rx, ry)
            dcls = manhattan(ox, oy, rx, ry)
            diff = dcls - dself  # lower is better (more negative => we are closer)
            if dself < self_best:
                self_best = dself
            if diff < diff_best or (diff == diff_best and dself < self_best):
                diff_best = diff
                opp_best = dcls
        # Secondary: minimize our distance to some resource; also avoid getting too close to opponent overall
        opp_to_self = manhattan(nx, ny, ox, oy)
        key = (diff_best, self_best, opp_best, opp_to_self, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]