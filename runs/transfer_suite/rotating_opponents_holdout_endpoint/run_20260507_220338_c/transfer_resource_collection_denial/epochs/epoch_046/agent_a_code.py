def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(p) for p in (observation.get("resources", []) or []) if tuple(p) not in obstacles]
    if not resources:
        return [0, 0]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        ax = x1 - x2; ax = -ax if ax < 0 else ax
        ay = y1 - y2; ay = -ay if ay < 0 else ay
        return ax if ax >= ay else ay

    # Choose the resource with maximum contest advantage (opponent takes longer than we do).
    best_res = None
    best_adv = -10**9
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = (opd - myd) * 1000 - myd  # prioritize winning races, then closeness
        if adv > best_adv:
            best_adv = adv
            best_res = (rx, ry)

    tx, ty = best_res
    # If opponent is already at same distance or closer, bias toward blocking by moving closer anyway
    # and prefer moves that increase our distance relative to opponent.
    best_move = (0, 0); best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd1 = cheb(nx, ny, tx, ty)
        opd0 = cheb(ox, oy, tx, ty)
        # Rough "opponent race" pressure: reward states where we look faster, penalize giving opponent free advantage.
        val = (opd0 - myd1) * 1200 - myd1
        # Add small bias to reduce our distance to target and increase our distance from opponent when racing is tight.
        val += -cheb(nx, ny, tx, ty) * 2
        val += cheb(nx, ny, ox, oy) * 0.5
        # Deterministic tie-break: prefer staying still last in move ordering.
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]