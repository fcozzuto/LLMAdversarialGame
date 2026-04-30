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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

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

    # Target selection: maximize how much closer we are than opponent.
    bestT = None
    bestM = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        margin = do - ds  # positive means we are closer or tie-favored
        score = margin * 1000 - ds  # deterministic preference
        if bestM is None or score > bestM or (score == bestM and (tx, ty) < bestT):
            bestM = score
            bestT = (tx, ty)

    # If no resources, stay.
    if bestT is None:
        return [0, 0]
    tx, ty = bestT

    # Move selection: improve our approach to target while preventing opponent snatching.
    bestMove = (0, 0)
    bestVal = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        # Extra: if opponent is also close, bias toward increasing separation.
        sep = cheb(nx, ny, ox, oy)
        oppSepNow = cheb(sx, sy, ox, oy)

        val = ds2 * 3 - (do2 - ds2) * 8 - sep * 0.3
        # If we would be worse than staying in terms of approach, add penalty.
        curDs = cheb(sx, sy, tx, ty)
        if ds2 > curDs:
            val += (ds2 - curDs) * 2
        # Prefer moves that increase separation from opponent when margins are small.
        if (do2 - cheb(sx, sy, tx, ty)) <= 1 and sep < oppSepNow:
            val += 1.5

        if bestVal is None or val < bestVal or (val == bestVal and (dx, dy) < bestMove):
            bestVal = val
            bestMove = (dx, dy)

    return [int(bestMove[0]), int(bestMove[1])]