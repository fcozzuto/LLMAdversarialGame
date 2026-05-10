def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obstacles.add((int(a[0]), int(a[1])))

    srole = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in srole) or ("evade" in srole)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def obst_adj_pen(x, y):
        pen = 0
        for dx, dy in moves:
            if (x + dx, y + dy) in obstacles:
                pen += 1
        return pen

    # center bias for evader to avoid being funneled to corners
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_to_opp = cheb(nx, ny, ox, oy)
        if not is_evader:
            if nx == ox and ny == oy:
                score = -10**9
            else:
                score = d_to_opp * 100 + obst_adj_pen(nx, ny) * 7
                # slight preference to keep pressure on same side (reduce opponent escape)
                score += abs((nx - ox)) * 2 + abs((ny - oy)) * 2
        else:
            if nx == ox and ny == oy:
                score = 10**9
            else:
                # maximize distance from pursuer, then avoid obstacles, then stay near center
                score = -d_to_opp * 100 - obst_adj_pen(nx, ny) * 3 + (abs(nx - cx) + abs(ny - cy)) * 0.5

        if best_score is None or (score < best_score if not is_evader else score < best_score):
            best_score = score
            best_move = [dx, dy]

    return best_move