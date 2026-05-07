def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for o in obstacles_list:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
    if not res:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Pick target: earlier arrival advantage for us; tie-breaker by proximity.
    best = None
    best_key = None
    for rx, ry in res:
        my_d = abs(rx - sx) + abs(ry - sy)
        opp_d = abs(rx - ox) + abs(ry - oy)
        key = (my_d - opp_d, my_d, abs(rx - (w - 1 - ox)) + abs(ry - (h - 1 - oy)))
        if best_key is None or key < best_key:
            best_key, best = key, (rx, ry)

    tx, ty = best

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    # Evaluate one-step moves toward the chosen target while avoiding obstacles.
    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        my_d2 = abs(tx - nx) + abs(ty - ny)
        opp_d2 = abs(tx - ox) + abs(ty - oy)
        # Encourage reaching target and keeping advantage over opponent; slight obstacle aversion.
        score = (my_d2 - opp_d2, my_d2, abs(tx - nx) + abs(ty - ny))
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]