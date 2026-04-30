def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def d(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp = (ox, oy)

    def legal_steps():
        out = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obstacles and (nx, ny) != opp:
                out.append((dx, dy, nx, ny))
        return out

    legal = legal_steps()
    if not legal:
        return [0, 0]

    # Strategic change: choose a target that is safe from opponent (maximize opponent distance),
    # while still reasonably reachable from us (minimize our distance with that constraint).
    if resources:
        best_t = None
        best_pair = None
        for r in resources:
            od = d(opp, r)
            sd = d((sx, sy), r)
            pair = (-od, sd, r[0], r[1])  # deterministic tie-break
            if best_pair is None or pair < best_pair:
                best_pair = pair
                best_t = r
    else:
        best_t = None

    def score_move(nx, ny, dx, dy):
        s = 0
        # Strongly avoid getting boxed: keep distance from opponent.
        s -= 4.0 * d((nx, ny), opp)

        if best_t is not None:
            before = d((sx, sy), best_t)
            after = d((nx, ny), best_t)
            s += 5.0 * (before - after)  # move progress toward safe target
            # Also discourage moves that improve opponent's access to our chosen target.
            opp_after = (ox + dx, oy + dy)
            if inside(opp_after[0], opp_after[1]) and opp_after not in obstacles and opp_after != (nx, ny):
                s -= 2.5 * (d(opp_after, best_t) - d(opp, best_t))

        # If we can capture by stepping onto opponent (engine would reject capture-square, but include penalty anyway)
        if (nx, ny) == opp:
            s -= 10000

        # Slight preference to avoid edges only when tied (deterministic).
        s -= 0.01 * (nx + ny)
        return s

    best = None
    best_s = None
    for dx, dy, nx, ny in legal:
        sc = score_move(nx, ny, dx, dy)
        key = (-sc, dx, dy, nx, ny)  # deterministic
        if best_s is None or key < best_s:
            best_s = key
            best = [dx, dy]
    return [int(best[0]), int(best[1])]