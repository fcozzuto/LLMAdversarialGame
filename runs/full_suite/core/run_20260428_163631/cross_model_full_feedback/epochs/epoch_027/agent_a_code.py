def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            x = int(p[0]); y = int(p[1])
            if inb(x, y): obst.add((x, y))
        except:
            pass

    res = []
    for r in (observation.get("resources", []) or []):
        try:
            x = int(r[0]); y = int(r[1])
            if inb(x, y) and (x, y) not in obst:
                res.append((x, y))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = dx if dx >= 0 else -dx
        dy = ay - by; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy

    rem = int(observation.get("remaining_resource_count", len(res)) or len(res))
    close_phase = (rem <= 6)
    block_phase = (rem <= 4)

    best_target = None
    best_score = None
    for tx, ty in res:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer resources we can reach sooner; if we're behind, favor blocking nearer to opponent.
        if block_phase and do < ds:
            bias = 0.6
        else:
            bias = 1.0
        score = (ds * bias) + (0.15 if (tx + ty) % 2 == 0 else 0.0) + (0.01 * (tx - ty) if (tx >= ty) else -0.01 * (ty - tx))
        if best_score is None or score < best_score:
            best_score = score
            best_target = (tx, ty)

    tx, ty = best_target
    # If still close to multiple choices, optionally bias away from opponent to reduce collisions.
    opp_cheb = cheb(sx, sy, ox, oy)

    best_move = (0, 0)
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(nx, ny, ox, oy)
        # Small deterministic tie-break by position parity.
        parity = 0.05 if (nx + ny) % 2 == 0 else 0.0
        val = ds2 + parity
        # During late game, discourage moves that let opponent get much closer (a mild block).
        if close_phase:
            val += (0.25 if do2 > opp_cheb else -0.15)
        # Also, if we're behind the target, try to keep distance reduction smaller (tighter approach).
        if block_phase:
            dso = cheb(ox, oy, tx, ty)
            if dso < cheb(sx, sy, tx, ty):
                val += 0.3 * (do2 - opp_cheb)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]