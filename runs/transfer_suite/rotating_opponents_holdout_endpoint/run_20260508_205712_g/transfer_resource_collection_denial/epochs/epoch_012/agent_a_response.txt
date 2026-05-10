def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    resources = [tuple(r) for r in observation.get("resources", [])]
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    my = (sx, sy)
    opp = (ox, oy)
    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for r in resources:
        if r in obstacles:
            continue
        dS = cheb(my, r)
        dO = cheb(opp, r)
        lead = 1 if dS <= dO else 0
        key = (lead, -(dO - dS), -dO, dS, -r[0], -r[1])
        if best_key is None or key > best_key:
            best_key = key
            best = r

    tx, ty = best

    bestm = (0, 0)
    bestmk = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my2 = (nx, ny)
        dS2 = cheb(my2, (tx, ty))
        dO2 = cheb(opp, (tx, ty))
        # Prefer reducing our distance; if tied, prefer moves that worsen opponent's situation.
        # Also slightly prefer progressing toward target coordinates to avoid loops.
        prog = abs(nx - tx) + abs(ny - ty)
        k = (-dS2, dO2 - dS2, -prog, dx, dy)
        if bestmk is None or k > bestmk:
            bestmk = k
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]