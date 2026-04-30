def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set((p[0], p[1]) for p in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in blocked
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    viable = []
    for r in resources:
        rx, ry = r[0], r[1]
        if not legal(rx, ry): 
            continue
        myd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can beat; then simply closer; then stable tiebreak.
        margin = od - myd
        viable.append((margin, -myd, abs((rx + ry) - (sx + sy)), -rx, -ry, rx, ry))
    viable.sort(reverse=True)
    if viable:
        _, _, _, _, _, tx, ty = viable[0]
    else:
        # No legal resources: drift diagonally away from opponent while heading to center-ish.
        cx, cy = w // 2, h // 2
        tx, ty = cx, cy

    best = (0, 0); best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        contested = od2 <= myd2
        # Score: win chance, then progress to target, then avoid letting opponent close.
        val = 0
        val += (1 if od2 - myd2 > 0 else -1) * 1000
        val += (od2 - myd2) * 20
        val += (-myd2) * 3
        # If contested, prioritize increasing opponent distance; else keep pushing target.
        dist_opp = cheb(nx, ny, ox, oy)
        val += dist_opp * (2 if contested else 1)
        # Mild obstacle avoidance: prefer tiles with fewer blocked neighbors.
        bad = 0
        for ax, ay in moves:
            px, py = nx + ax, ny + ay
            if not inb(px, py) or (px, py) in blocked:
                bad += 1
        val += -bad * 0.2
        # Deterministic tie-break by move order and coordinates.
        tie = (val, -dx, -dy, nx, ny)
        if best_val is None or tie > best_val:
            best_val = tie
            best = (dx, dy)
    return [int(best[0]), int(best[1])]