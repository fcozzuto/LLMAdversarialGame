def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def opp_best_dist(tx, ty):
        best = None
        for dx, dy in dirs:
            nx, ny = ox + dx, oy + dy
            if not legal(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            if best is None or d < best:
                best = d
        return best if best is not None else man(ox, oy, tx, ty)

    if not resources:
        cx, cy = w // 2, h // 2
        best = None
        bd = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            score = -man(nx, ny, cx, cy)
            if bd is None or score > bd:
                bd = score
                best = (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        my_next = (nx, ny)
        # Evaluate by targeting the resource that gives the biggest advantage
        # (opponent farther than me, accounting for opponent's next greedy response).
        val = -10**9
        for rx, ry in resources:
            my_d = man(my_next[0], my_next[1], rx, ry)
            opp_d = opp_best_dist(rx, ry)
            # Larger is better: how much closer I get relative to opponent.
            # Small tie-breaker: prefer closer overall to the resource.
            gain = (opp_d - my_d) * 10 - my_d
            if gain > val:
                val = gain

        # Extra shaping: slightly prefer staying nearer to resources overall
        # and away from being cornered by obstacles (use center as mild bias).
        val += -0.2 * man(nx, ny, w // 2, h // 2)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]