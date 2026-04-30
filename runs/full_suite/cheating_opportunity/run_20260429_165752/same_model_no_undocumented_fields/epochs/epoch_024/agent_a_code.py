def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose resource where we are relatively closer than opponent.
    best = None
    bestscore = None
    for x, y in resources:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        score = do - ds  # higher means opponent farther relative to us
        if bestscore is None or score > bestscore or (score == bestscore and ds < cheb(sx, sy, ox, oy)):
            bestscore = score
            best = (x, y)
    if best is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best

    # One-step decision: head to target while maximizing distance from opponent.
    bestm = (0, 0)
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dv = cheb(nx, ny, tx, ty)
        dist_opp = cheb(nx, ny, ox, oy)
        # Prefer being closer to target; among them, prefer farther from opponent; then prefer staying (closer to our current).
        val = (-dv, -dist_opp, cheb(nx, ny, sx, sy))
        if bestv is None or val > bestv:
            bestv = val
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]