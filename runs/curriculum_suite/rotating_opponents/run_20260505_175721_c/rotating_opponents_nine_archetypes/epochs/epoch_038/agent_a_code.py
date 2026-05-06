def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def best_adv(px, py):
        best = -10**9
        best_t = resources[0]
        for tx, ty in resources:
            myd = man(px, py, tx, ty)
            opd = man(ox, oy, tx, ty)
            adv = (opd - myd)  # positive if we are closer
            if adv > best or (adv == best and myd < man(px, py, best_t[0], best_t[1])):
                best = adv
                best_t = (tx, ty)
        return best, best_t

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        adv, t = best_adv(nx, ny)
        # Encourage approaching a chosen target and increasing separation from opponent.
        myd = man(nx, ny, t[0], t[1])
        sep = man(nx, ny, ox, oy)
        score = 10 * adv - myd + 0.1 * sep
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            # Deterministic tie-break: prefer staying still, then smaller |dx|+|dy|, then lexicographic.
            cand = dx, dy
            cur = best_move[0], best_move[1]
            if (cand == (0, 0) and cur != (0, 0)) or \
               (abs(cand[0]) + abs(cand[1]) < abs(cur[0]) + abs(cur[1])) or \
               (abs(cand[0]) + abs(cand[1]) == abs(cur[0]) + abs(cur[1]) and cand < cur):
                best_move = [dx, dy]
    return best_move