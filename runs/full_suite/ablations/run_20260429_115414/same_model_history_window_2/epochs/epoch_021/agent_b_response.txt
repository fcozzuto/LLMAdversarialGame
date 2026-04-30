def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    remaining = observation.get("remaining_resource_count", len(resources))

    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources or remaining <= 0:
        best = (0, 0); bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = 2.0 * cheb(nx, ny, sx, sy) - 1.0 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # Pick a target resource we are likely to reach first (deterministic, no search)
    best_target = None; best_tv = -10**18
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        if d_me == 0:
            best_target = (rx, ry); best_tv = 10**18
            break
        # Prefer resources where we are closer; otherwise avoid likely opponent steals.
        closer_bonus = 30.0 if d_me < d_op else 0.0
        tv = closer_bonus - 2.0 * d_me + 0.5 * (d_op - d_me)
        # Slightly prefer resources farther from opponent to reduce contention later.
        tv += 0.03 * d_op
        if tv > best_tv:
            best_tv = tv; best_target = (rx, ry)

    tx, ty = best_target
    best_move = (0, 0); best_mv = -10**18
    for dx, dy, nx, ny in legal:
        d_after = cheb(nx, ny, tx, ty)
        d_opp_after = cheb(nx, ny, ox, oy)
        on_res = 1 if (nx, ny) == (tx, ty) else 0
        # Move toward target while keeping distance from opponent (new behavior vs simple chase-only).
        mv = 1000.0 * on_res - 3.0 * d_after + 0.25 * d_opp_after
        # If opponent is already closer to target, prioritize cutting off by minimizing our distance to it less aggressively and distancing.
        d_me_now = cheb(sx, sy, tx, ty)
        d_op_now = cheb(ox, oy, tx, ty)
        if d_me_now >= d_op_now:
            mv += 0.6 * d_opp_after - 1.0 * d_after
        if mv > best_mv:
            best_mv = mv; best_move = (dx, dy)

    return [best_move[0], best_move[1]]