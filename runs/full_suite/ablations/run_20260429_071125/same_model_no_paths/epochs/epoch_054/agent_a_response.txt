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
    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose a target resource: closest with a small advantage to "safer" ones
    # (more distance from opponent reduces contest pressure).
    if resources:
        best = None
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # score: minimize (my distance), but prefer resources where opponent is farther
            key = (d_me, -(d_op - d_me))
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        # If no resources known, move to stay central-ish while keeping distance from opponent
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0

    # Pick move that reduces distance to target; tie-break by maximizing distance from opponent.
    best_move = (10**9, -1, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_to = cheb(nx, ny, int(tx), int(ty))
        d_opp = cheb(nx, ny, ox, oy)
        # tie-break deterministic by fixed secondary criteria
        tie = (0 if (dx == 0 and dy == 0) else 1)
        cand = (d_to, -d_opp, -tie, dx, dy)
        if cand[0] < best_move[0] or (cand[0] == best_move[0] and cand[1] < best_move[1]) or \
           (cand[0] == best_move[0] and cand[1] == best_move[1] and cand[2] < best_move[2]):
            best_move = (cand[0], cand[1], cand[2], cand[3], cand[4])

    return [int(best_move[3]), int(best_move[4])]