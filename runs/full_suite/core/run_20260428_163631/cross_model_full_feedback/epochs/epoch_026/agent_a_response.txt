def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles", []) or []:
        x, y = p[0], p[1]
        x = int(x); y = int(y)
        if inb(x, y): obst.add((x, y))

    res = []
    for r in observation.get("resources", []) or []:
        x, y = r[0], r[1]
        x = int(x); y = int(y)
        if inb(x, y) and (x, y) not in obst:
            res.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = dx if dx >= 0 else -dx
        dy = ay - by; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy

    remaining = int(observation.get("remaining_resource_count", len(res)) or len(res))
    if not res:
        return [0, 0]

    # Pick a target we're comparatively closer to; tie-break deterministically.
    bestT = None
    bestKey = None
    for (rx, ry) in res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (do - ds, -ds, rx, ry)  # maximize advantage; then closer; then lex
        if bestKey is None or key > bestKey:
            bestKey = key
            bestT = (rx, ry)
    tx, ty = bestT

    # If opponent is clearly closer to the chosen target, prioritize increasing their distance (blocking).
    opp_margin = cheb(ox, oy, tx, ty) - cheb(sx, sy, tx, ty)

    bestMove = legal[0]
    bestVal = None
    for dx, dy in legal:
        nsx, nsy = sx + dx, sy + dy
        d_s_next = cheb(nsx, nsy, tx, ty)
        d_o = cheb(ox, oy, tx, ty)
        val = 0
        # Primary: move towards target; stronger when we are at/near the lead.
        if opp_margin >= 2:
            # Block: maximize opponent's relative standing next (their distance unchanged, so push ourselves away from alternative not needed).
            # Better: minimize our distance while maximizing reduced "advantage" for them next by moving to a cell that is worse for them to leave.
            # Approx: maximize our distance from opponent and towards target? Deterministic and safe.
            val = (-d_s_next, -cheb(nsx, nsy, ox, oy), dx, dy)
        else:
            # Lead mode: minimize our distance to target; also keep away from opponent a bit to avoid grabs colliding.
            val = (-d_s_next, -cheb(nsx, nsy, ox, oy), dx, dy)

        if bestVal is None or val > bestVal:
            bestVal = val
            bestMove = (dx, dy)

    return [int(bestMove[0]), int(bestMove[1])]