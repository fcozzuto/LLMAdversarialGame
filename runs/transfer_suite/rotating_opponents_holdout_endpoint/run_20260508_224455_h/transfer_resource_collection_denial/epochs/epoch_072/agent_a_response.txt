def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Choose the resource where we are most ahead (positive race), tie-break by being closer.
    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        race = od - sd
        cand = (race, -sd, -od, rx, ry)
        if best is None or cand > best:
            best = cand
    _, _, _, tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]

    # Evaluate candidate moves with a deterministic local score.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        myd = cheb(nx, ny, tx, ty)
        # Prefer moves that reduce distance to our target.
        progress = cheb(sx, sy, tx, ty) - myd

        # Also consider making it harder for opponent to reach the same target.
        oppd = cheb(ox, oy, tx, ty)
        # Opponent won't move yet, but our move can change contest indirectly via timing; use spacing heuristic.
        contest = oppd - myd

        # Slightly prefer moves toward general resource density (closest resource).
        mind = 10**9
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            d = cheb(nx, ny, rx, ry)
            if d < mind:
                mind = d

        score = 1000 * progress + 50 * contest - 2 * myd - mind
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]