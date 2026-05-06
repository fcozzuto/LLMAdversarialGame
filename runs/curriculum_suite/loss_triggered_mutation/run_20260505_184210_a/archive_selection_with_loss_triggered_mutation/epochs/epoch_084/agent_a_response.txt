def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    me = (sx, sy)
    opp = (ox, oy)

    # Opportunistic/Interceptor target selection: prefer resources we can reach no later than opponent,
    # with a bias to those where we have an advantage.
    best = None
    best_key = None
    for r in resources:
        sd = man(me, r)
        od = man(opp, r)
        can_contest = 1 if sd <= od else 0
        # Lower is better: contest-first, then maximize advantage (via negative), then closeness and coords.
        key = (-can_contest, sd - 0.75 * od, sd, r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best = r
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Deterministic move: choose among valid neighbors the one minimizing (distance to target, and
    # also a small penalty if it increases opponent's distance advantage).
    bestm = [0, 0]
    bestmk = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        ns = (nx, ny)
        dts = man(ns, (tx, ty))
        dtop = man(opp, (tx, ty))
        # If we are closer or equal, lightly prefer staying closer; if not, don't waste moves.
        contest_pen = 0 if man(ns, (tx, ty)) <= dtop else 1
        key = (contest_pen, dts, abs(nx - tx) + abs(ny - ty), abs(nx - ox) + abs(ny - oy), dx, dy)
        if bestmk is None or key < bestmk:
            bestmk = key
            bestm = [dx, dy]

    return bestm if bestmk is not None else [0, 0]