def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        best = None
        bestv = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            # Prefer moves that increase distance from opponent while staying in-bounds
            v = cheb(nx, ny, ox, oy)
            if best is None or v > bestv or (v == bestv and (dx, dy) < best):
                best, bestv = (dx, dy), v
        return [best[0], best[1]]

    # Choose move that best secures contested resources: maximize (opp_dist - my_dist),
    # then minimize my_dist to the best candidate, then distance-to-center tie-break.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = (0, 0)
    best_score = None
    best_tie = None

    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        my_best = 10**9
        opp_best = 10**9
        diff_best = -10**9
        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            diff = d_opp - d_my
            if diff > diff_best or (diff == diff_best and (d_my < my_best or (d_my == my_best and d_opp < opp_best))):
                diff_best, my_best, opp_best = diff, d_my, d_opp

        # primary: diff_best (bigger is better), secondary: my_best (smaller), tertiary: deterministic tie
        score = (diff_best, -my_best)
        tie = abs(nx - cx) + abs(ny - cy)
        if best_score is None or score > best_score or (score == best_score and (tie < best_tie or (tie == best_tie and (dx, dy) < best_move))):
            best_move, best_score, best_tie = (dx, dy), score, tie

    return [best_move[0], best_move[1]]