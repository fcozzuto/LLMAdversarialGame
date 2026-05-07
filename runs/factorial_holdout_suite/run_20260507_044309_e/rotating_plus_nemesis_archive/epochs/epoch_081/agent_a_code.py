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
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                v = (cheb(nx, ny, cx, cy), nx, ny)
                if best is None or v < best[0]:
                    best = (v, [dx, dy])
        return best[1] if best else [0, 0]

    scored = []
    for rx, ry in resources:
        dself = cheb(sx, sy, rx, ry)
        dop = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; if tied, prefer those opponent is farther from.
        # Deterministic tie-break: smaller (dself), larger (dop-dself), then lexicographic.
        key = (dself, -(dop - dself), rx, ry)
        scored.append((key, (rx, ry)))
    scored.sort(key=lambda t: t[0])
    tx, ty = scored[0][1]

    def step_score(nx, ny):
        # Lower is better; encourage approaching target, penalize obstacles and away-moves.
        return (cheb(nx, ny, tx, ty), cheb(nx, ny, ox, oy), nx, ny)

    candidates = []
    best_move = None
    best_s = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            s = step_score(nx, ny)
            if best_s is None or s < best_s:
                best_s = s
                best_move = [dx, dy]
            candidates.append((s, [dx, dy]))

    # If something is off-grid/blocked, still choose a deterministic safe move (or stay).
    if best_move is not None:
        return best_move

    return [0, 0]