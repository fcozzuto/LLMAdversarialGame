def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx*dx + dy*dy

    # Choose target: prioritize being closer than opponent; tie-break deterministically
    if resources:
        best = None
        best_key = None
        for r in resources:
            tx, ty = r[0], r[1]
            myd = d2(sx, sy, tx, ty)
            opd = d2(ox, oy, tx, ty)
            adv = opd - myd  # positive if I'm closer
            key = (-(adv >= 0), -adv, myd, tx, ty)  # prefer adv>=0, larger adv, smaller myd
            if best_key is None or key < best_key:
                best_key = key
                best = (tx, ty)
        tx, ty = best
    else:
        # Drift toward center while slightly denying opponent lane
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        myd = d2(nx, ny, tx, ty)
        oppd = d2(ox, oy, tx, ty)

        # Score: minimize my distance; strongly prefer increasing closeness advantage; avoid proximity to obstacles
        score = myd - 1.5 * (oppd - myd)
        # obstacle proximity penalty (check neighbors)
        prox = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                cx, cy = nx + ax, ny + ay
                if (cx, cy) in obstacles:
                    prox += 1
        score += 3.0 * prox

        # Mild tie-break: move away from opponent if not harming distance too much
        opp_next = d2(nx, ny, ox, oy)
        score += 0.01 * (-opp_next)

        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]