def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (7, 7))
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = obstacles_list if isinstance(obstacles_list, set) else set(tuple(p) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Pick best resource: maximize how much closer we are than opponent (tie-break deterministically)
    best = None
    for rx, ry in resources:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        score = (do - ds, -ds, -abs(rx - 0) - abs(ry - 0), rx, ry)
        if best is None or score > best[0]:
            best = (score, (rx, ry))
    tx, ty = best[1]

    def valid_moves(px, py):
        mv = []
        for dx, dy in deltas:
            nx, ny = px + dx, py + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                mv.append((dx, dy, nx, ny))
        if not mv:
            return [(0, 0, px, py)]
        # deterministic order
        mv.sort(key=lambda t: (abs(t[2] - tx) + abs(t[3] - ty), abs(t[0]) + abs(t[1]), t[0], t[1]))
        return mv

    my_moves = valid_moves(sx, sy)

    # Predict opponent greedy toward same target
    opp_moves = valid_moves(ox, oy)
    opp_best = opp_moves[0]
    for dx, dy, nx, ny in opp_moves:
        d = abs(tx - nx) + abs(ty - ny)
        cur = abs(tx - opp_best[2]) + abs(ty - opp_best[3])
        if d < cur or (d == cur and (dx, dy) < (opp_best[0], opp_best[1])):
            opp_best = (dx, dy, nx, ny)

    _, _, oxn, oyn = opp_best
    best_move = (0, 0, sx, sy)
    for dx, dy, nx, ny in my_moves:
        my_d = abs(tx - nx) + abs(ty - ny)
        opp_d = abs(tx - oxn) + abs(ty - oyn)
        # maximize our advantage after both moves; tie-break by closer to target then deterministic
        key = (opp_d - my_d, -my_d, dx, dy, nx, ny)
        if key > (abs(tx - best_move[2]) + abs(ty - best_move[3]), -(abs(tx - best_move[2]) + abs(ty - best_move[3])), best_move[0], best_move[1], best_move[2], best_move[3]):
            best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]