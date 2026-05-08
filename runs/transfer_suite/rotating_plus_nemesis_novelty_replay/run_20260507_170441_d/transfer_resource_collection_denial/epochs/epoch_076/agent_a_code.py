def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obst.add((p[0], p[1]))
    res_set = set((r[0], r[1]) for r in resources)
    if not resources:
        return [0, 0]

    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    best_move = [0, 0]
    best_score = None
    turn = observation.get("turn_index", 0)

    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        bonus = 20 if (nx, ny) in res_set else 0

        best_adv = -10**9
        for rx, ry in resources:
            myd = dist8(nx, ny, rx, ry)
            opd = dist8(ox, oy, rx, ry)
            adv = opd - myd
            if adv > best_adv:
                best_adv = adv

        score = bonus + best_adv * 10 - dist8(nx, ny, ox, oy)
        tie = (turn + i) % 7  # deterministic tie-break
        if best_score is None or score > best_score or (score == best_score and tie < best_tie):
            best_score = score
            best_tie = tie
            best_move = [dx, dy]

    return best_move