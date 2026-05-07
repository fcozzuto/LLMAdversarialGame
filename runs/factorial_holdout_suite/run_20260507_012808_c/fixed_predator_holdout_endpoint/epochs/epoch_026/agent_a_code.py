def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx, sy, ox, oy = 0, 0, 0, 0

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    res_set = set()
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                if (x, y) not in res_set:
                    res_set.add((x, y))
                    resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        moves.sort(key=lambda t: (abs(t[0])+abs(t[1]), t[0], t[1]))
        return [moves[0][0], moves[0][1]]

    def stepdist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    best_move = None
    best_key = None
    for dx, dy in sorted(moves, key=lambda t: (t[0], t[1])):
        nx, ny = sx + dx, sy + dy
        collected = 1 if (nx, ny) in res_set else 0

        self_best = 10**9
        opp_best = 10**9
        for rx, ry in resources:
            d1 = stepdist((nx, ny), (rx, ry))
            if d1 < self_best:
                self_best = d1
            d2 = stepdist((ox, oy), (rx, ry))
            if d2 < opp_best:
                opp_best = d2

        adv = opp_best - self_best
        # Bonus for moving to reduce distance to nearest resource vs current
        cur_best = 10**9
        for rx, ry in resources:
            d0 = stepdist((sx, sy), (rx, ry))
            if d0 < cur_best:
                cur_best = d0
        improve = cur_best - self_best

        key = (collected, adv, improve, -self_best, -(abs(nx - ox) + abs(ny - oy)), -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]