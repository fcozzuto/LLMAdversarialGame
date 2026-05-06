def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Target selection: prefer resources where we arrive earlier; otherwise pick ones that are very bad for opponent.
    best = None
    best_key = None
    for t in resources:
        d1 = cheb((sx, sy), t)
        d2 = cheb((ox, oy), t)
        win_margin = d2 - d1  # positive means we closer
        # Deterministic tie-break by coordinates.
        key = (-(win_margin), d1, d2, t[0], t[1])
        if best_key is None or key < best_key:
            best_key, best = key, t

    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_eval = None
    # Greedy move with light local lookahead and obstacle/bounds avoidance.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        my_d = cheb((nx, ny), (tx, ty))
        opp_d = cheb((ox, oy), (tx, ty))
        # If we can still beat opponent, prioritize progress; else, increase their distance.
        eval_key = (my_d - (opp_d - my_d) * 0.5, my_d, -opp_d, nx, ny)
        if best_eval is None or eval_key < best_eval:
            best_eval, best_move = eval_key, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]