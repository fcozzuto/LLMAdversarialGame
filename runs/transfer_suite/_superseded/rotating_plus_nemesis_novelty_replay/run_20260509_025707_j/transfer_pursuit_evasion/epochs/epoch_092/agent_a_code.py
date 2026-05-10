def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # opponent prediction: greedy evasion from our candidate position
    def predict_opp(ax, ay):
        best = None
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = ox + dx, oy + dy
            if not valid(nx, ny):
                continue
            d = manh((nx, ny), (ax, ay))
            if d > best_val:
                best_val = d
                best = (nx, ny)
        return best if best is not None else (ox, oy)

    best_move = (0, 0)
    best_score = 10**18
    # tie-breaks: capture > distance > "cornering" (lower own escape space) > deterministic order
    for i, (dx, dy) in enumerate(dirs):
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nox, noy = predict_opp(nx, ny)
        if (nx, ny) == (nox, noy):
            return [dx, dy]
        dist = manh((nox, noy), (nx, ny))

        # count open neighbors from opponent position after prediction (fewer options is better for us)
        open_cnt = 0
        for ddx, ddy in dirs:
            px, py = nox + ddx, noy + ddy
            if valid(px, py):
                open_cnt += 1

        score = (dist, -open_cnt, i)
        if score < (best_score, 0, 0):
            best_score = dist
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]