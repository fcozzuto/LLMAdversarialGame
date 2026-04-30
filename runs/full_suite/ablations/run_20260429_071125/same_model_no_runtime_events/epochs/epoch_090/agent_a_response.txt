def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not ok(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Pick a visible resource we can contest (prefer those closer than opponent); else nearest.
    target = None
    if resources:
        best = None
        for rx, ry in resources:
            d1 = cheb(sx, sy, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            # Big preference for contested resources (we are strictly closer); tie-broken by smaller d1.
            key = (0 if d1 < d2 else 1, d1, d2, rx + 31 * ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        target = best[1]

    # Fallback: head toward center while keeping distance from opponent.
    if target is None:
        target = (w // 2, h // 2)

    best_move = [0, 0]
    best_score = None
    cur_d = cheb(sx, sy, target[0], target[1])
    cur_opp = cheb(sx, sy, ox, oy)

    # Evaluate immediate move deterministically.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, target[0], target[1])
        opp_d = cheb(nx, ny, ox, oy)
        progress = cur_d - d  # positive is good
        # Encourage staying away from opponent, but prioritize resource progress.
        score = (progress * 1000) + (opp_d * 10) - (d * 3)
        if (best_score is None) or (score > best_score) or (score == best_score and (dx, dy) < tuple(best_move)):
            best_score = score
            best_move = [dx, dy]

    return best_move