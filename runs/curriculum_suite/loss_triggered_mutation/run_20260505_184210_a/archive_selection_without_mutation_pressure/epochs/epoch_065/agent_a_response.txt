def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in moves if inside(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    res_list = observation.get("resources") or []
    resources = [(r[0], r[1]) for r in res_list if isinstance(r, (list, tuple)) and len(r) == 2]
    if not resources:
        return [0, 0]

    def manhattan(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    best_dx, best_dy = legal[0]
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Choose a target resource that we can beat the opponent to (maximize slack).
        max_slack = -10**9
        min_our = 10**9
        for rx, ry in resources:
            our_d = manhattan(nx, ny, rx, ry)
            opp_d = manhattan(ox, oy, rx, ry)
            slack = opp_d - our_d  # positive => we are closer than opponent
            if slack > max_slack or (slack == max_slack and our_d < min_our):
                max_slack = slack
                min_our = our_d
        dist_to_opp = manhattan(nx, ny, ox, oy)
        # Primary: maximize slack; Secondary: minimize our distance; Tertiary: keep away from opponent.
        key = (-max_slack, min_our, -dist_to_opp, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_dx, best_dy = dx, dy

    return [best_dx, best_dy]