def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: man(ox, oy, c[0], c[1]) - 0.15 * man(sx, sy, c[0], c[1]))
        return [0 if tx == sx else (1 if tx > sx else -1), 0 if ty == sy else (1 if ty > sy else -1)]

    res = [(int(r[0]), int(r[1])) for r in resources]
    resource_set = set(res)

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        pos_bonus = 500 if (nx, ny) in resource_set else 0
        cur_best = -10**18

        for rx, ry in res:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer targets we can reach first / earlier, but keep some pressure even if contested.
            reach_adv = (od - sd)
            cont = -sd
            # Slight tie-break toward closer resources overall.
            s = 1200 * (1 if reach_adv > 0 else 0) + 10 * reach_adv + cont - 0.01 * (sd + od)
            if s > cur_best:
                cur_best = s

        score = pos_bonus + cur_best
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move