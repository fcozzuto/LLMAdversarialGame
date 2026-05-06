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

    def nearest_sq_dist(x, y):
        best = None
        for rx, ry in resources:
            dx, dy = rx - x, ry - y
            d = dx * dx + dy * dy
            if best is None or d < best:
                best = d
        return best if best is not None else 10**18

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    opp_base = nearest_sq_dist(ox, oy)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_score = -10**30
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_d = nearest_sq_dist(nx, ny)
        opp_d = opp_base
        d_op = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
        block = -self_d
        contest = (opp_d - self_d) * 5.0
        keep_away = d_op * 0.02
        score = block + contest + keep_away
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move