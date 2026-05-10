def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
        if (tx == ox or ty == oy) and (sx, sy) == (0, 0):
            pass
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    res = [(int(x), int(y)) for x, y in resources]

    # Choose best resource by "arrival advantage": how much earlier we are vs opponent
    best_rx, best_ry = res[0]
    best_target_val = -10**18
    for rx, ry in res:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # Encourage winning the contest first; then minimize own distance; slight preference for nearer to opponent too
        val = (od - sd) * 1000 - sd + (od - sd)
        if val > best_target_val:
            best_target_val = val
            best_rx, best_ry = rx, ry

    # Pick a move that maximizes expected improvement toward that target and preserving advantage vs opponent
    cur_sd = dist(sx, sy, best_rx, best_ry)
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = dist(nx, ny, best_rx, best_ry)
        my_adv = dist(ox, oy, best_rx, best_ry) - nd  # opponent arrival advantage after our move
        # Main objective: reduce our distance; secondary: keep advantage
        score = (cur_sd - nd) * 50 + my_adv * 10 - dist(nx, ny, best_rx, best_ry)
        # Small deterministic bias to avoid oscillation: prefer not moving away from target
        if score > best_score or (score == best_score and (dx, dy) == (0, 0)):
            best_score = score
            best_move = [dx, dy]

    return best_move if valid(sx + best_move[0], sy + best_move[1]) else [0, 0]