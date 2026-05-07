def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    if not resources:
        # drift to improve distance from opponent (deterministic)
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            sc = -md((nx, ny), (ox, oy))
            if best is None or sc > best[0] or (sc == best[0] and (dx, dy) < (best[1], best[2])):
                best = (sc, dx, dy)
        return [best[1], best[2]]

    # choose resource maximizing (opponent_progress_over_us, then closeness)
    best_res = None
    best_key = None
    for r in resources:
        sd = md((sx, sy), r)
        od = md((ox, oy), r)
        key = (od - sd, -sd, r[0], r[1])
        if best_key is None or key > best_key:
            best_key = key
            best_res = r

    tx, ty = best_res

    # move greedily toward target; slight preference to deny if opponent is closer
    deny = (md((ox, oy), (tx, ty)) <= md((sx, sy), (tx, ty)))
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        self_d = md((nx, ny), (tx, ty))
        opp_d = md((ox, oy), (tx, ty))
        # If deny mode, prefer moves that reduce our distance more.
        sc = (-self_d, self_d, -opp_d if deny else 0, dx, dy)
        if best_score is None or sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]