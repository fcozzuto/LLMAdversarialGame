def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not valid(sx, sy):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Pick a resource with best "lead": (our_dist - opp_dist); also favor those nearer to finish.
    best = None
    best_key = None
    for rx, ry in resources:
        d1 = cheb(sx, sy, rx, ry)
        d2 = cheb(ox, oy, rx, ry)
        lead = d1 - d2  # negative is good (we are closer)
        # Break ties to encourage earlier capture: prioritize smaller our distance.
        key = (lead, d1, -rx - ry)  # deterministic tie-break
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    # If no resources, drift toward center-ish to create future tempo.
    if best is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best

    # Greedy one-step move with lookahead scoring; also discourage stepping near obstacles.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # obstacle proximity penalty
        prox = 0
        for ax, ay in deltas:
            xx, yy = nx + ax, ny + ay
            if 0 <= xx < w and 0 <= yy < h and (xx, yy) in obstacles:
                prox += 1
        # If target is contested, add a term to reduce distance advantage (race).
        d1_now = cheb(sx, sy, tx, ty)
        d2_now = cheb(ox, oy, tx, ty)
        contested = 1 if (d2_now <= d1_now) else 0
        score = (d_to_target * 10) + (prox * 2) - (d_opp * 0.05) - (contested * (0 if best is None else (cheb(ox, oy, tx, ty) - cheb(nx, ny, tx, ty))))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]