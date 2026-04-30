def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not free(sx, sy):
        for dx, dy in moves[1:]:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            # deterministic "kite" away from opponent while staying near center
            dc = cheb(nx, ny, w // 2, h // 2)
            do = cheb(nx, ny, ox, oy)
            score = (do, -dc)  # prefer larger distance from opponent
            if best is None or score > best[0]:
                best = (score, (dx, dy))
        return [best[1][0], best[1][1]]

    # Evaluate each move by aiming for a resource where we are more likely to arrive first,
    # while discouraging moves that give the opponent an advantage.
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # If we can take a resource this turn, do it.
        on_res = 1 if (nx, ny) in set(resources) else 0

        # Best prospective target from this new position: maximize (opponent_time - our_time),
        # then break ties by (our_time), then center proximity (slight).
        local_best = None
        for tx, ty in resources:
            t1 = cheb(nx, ny, tx, ty)
            t2 = cheb(ox, oy, tx, ty)
            advantage = t2 - t1  # positive means we arrive earlier
            # prefer not-yet-taken resources indirectly by time; deterministic tie-breaks
            cand = (advantage, -t1, -abs(tx - (w // 2)), -abs(ty - (h // 2)))
            if local_best is None or cand > local_best:
                local_best = cand

        # Add an explicit opponent-separation term to change behavior if margins are small.
        opp_sep = cheb(nx, ny, ox, oy)
        our_time_self = min(cheb(nx, ny, rx, ry) for (rx, ry) in resources)
        score = (on_res, local_best, opp_sep, -our_time_self)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]