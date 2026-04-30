def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose resource: prioritize ones we can reach sooner than opponent.
    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer being closer; secondary: overall closeness; tertiary: deterministic position.
            score = (ds - do, ds, rx, ry)
            if best is None or score < best[0]:
                best = (score, rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = 7 - sx, 7 - sy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    bestm = None
    for dx, dy, nx, ny in moves:
        d_to_target = cheb(nx, ny, tx, ty)
        d_from_opp = cheb(nx, ny, ox, oy)
        # Primary: reduce distance to target; Secondary: stay away from opponent; Tertiary: deterministic tie-break.
        mscore = (d_to_target, -d_from_opp, dx, dy)
        if bestm is None or mscore < bestm[0]:
            bestm = (mscore, dx, dy)

    return [int(bestm[1]), int(bestm[2])]