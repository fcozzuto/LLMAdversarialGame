def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Strategy change: pick a resource that maximizes our lead (opp - self), even if we're not currently closer.
    # Tie-break toward shorter travel for us and then toward the opponent side to race.
    best = None
    bestk = None
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        lead = do - ds  # positive => we are closer
        # prefer: bigger lead, then smaller ds, then further toward opponent corner
        corner_bias = (rx + ry) if (ox + oy) >= ((w - 1 - ox) + (h - 1 - oy)) else (-(rx + ry))
        k = (lead, -ds, corner_bias, -max(rx, ry), rx, ry)
        if bestk is None or k > bestk:
            bestk = k
            best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Choose step that most reduces our distance to the chosen target, avoiding obstacles.
    bestm = None
    bestmk = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = dist(nx, ny, tx, ty)
        # small tie: also slightly reduce opponent's distance to our target (deny race when possible)
        nod = dist(ox, oy, tx, ty)
        # Since opponent position doesn't change this turn, just add a deterministic preference for moves that push away from opponent.
        opp_push = dist(nx, ny, ox, oy)
        k = (-nd, opp_push, dx, dy)
        if bestmk is None or k > bestmk:
            bestmk = k
            bestm = (dx, dy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]