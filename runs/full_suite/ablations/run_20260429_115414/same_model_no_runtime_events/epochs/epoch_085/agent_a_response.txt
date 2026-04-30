def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Strategic target: maximize (oppDist - selfDist), so we prefer resources we can reach first.
    # If tied, choose smallest selfDist, then lexicographic.
    if res:
        best = None
        for rx, ry in res:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            cand = (adv, -sd, -rx, -ry)
            if best is None or cand > best[0]:
                best = (cand, rx, ry)
        rx, ry = best[1], best[2]
    else:
        # No visible resources: move to a stable contest point away from obstacles if possible.
        tx, ty = (w - 1 + 0) // 2, (h - 1 + 0) // 2
        if cheb(sx, sy, tx, ty) == cheb(ox, oy, tx, ty):
            # Nudge toward our corner to potentially grab unseen resources sooner.
            tx, ty = (0 if sx < ox else w - 1, 0 if sy < oy else h - 1)
        rx, ry = tx, ty

    best_move = [0, 0]
    best_score = None
    cur_d = cheb(sx, sy, rx, ry)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, rx, ry)

        # Prefer reducing distance to target; then avoid squares where opponent is much closer to the target.
        # Also penalize moving away.
        opp_nd = cheb(ox, oy, rx, ry)
        score = (cur_d - nd, -nd, (opp_nd - nd), -nx, -ny, -(abs(dx) + abs(dy)))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]