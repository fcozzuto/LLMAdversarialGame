def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        bestm, bestv = [0, 0], None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                v = (cheb(nx, ny, cx, cy), nx, ny)
                if bestv is None or v < bestv:
                    bestv, bestm = v, [dx, dy]
        return bestm

    scored = []
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we're at least not worse on; if worse, add a penalty.
        penalty = 0 if ds <= do else (ds - do + 1)
        scored.append((ds + penalty * 2, rx, ry, ds, do))
    scored.sort()
    _, tx, ty, _, _ = scored[0]

    bestm, bestv = [0, 0], None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        dnew = cheb(nx, ny, tx, ty)
        # Add small term to avoid moving into cells that make opponent much closer to same target.
        dop = cheb(ox, oy, tx, ty)
        v = (dnew, (0 if dnew <= dop else 1), nx, ny)
        if bestv is None or v < bestv:
            bestv, bestm = v, [dx, dy]
    return bestm