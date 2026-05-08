def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    best_t = None
    best_sc = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Big preference for resources we can reach first; then closer overall.
        sc = (do - ds) * 500 - ds * 10 + (rx * 0 + ry * 0)
        if do == ds:
            sc -= cheb(sx, sy, ox, oy) * 2
        if sc > best_sc:
            best_sc = sc
            best_t = (rx, ry)

    tx, ty = best_t
    cur_ds = cheb(sx, sy, tx, ty)

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    # Candidate move: deterministic choose from neighbor deltas that go closer to target when possible.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        nds = cheb(nx, ny, tx, ty)
        # Also estimate whether this moves us relative to opponent on the target.
        ndo = cheb(ox, oy, tx, ty)
        val = (cur_ds - nds) * 200 - nds * 3 + (ndo - nds) * 20
        # Prefer moves that avoid getting "stuck" adjacent to obstacles (minor).
        adj_obs = 0
        for ex, ey in [(nx-1, ny),(nx+1, ny),(nx, ny-1),(nx, ny+1)]:
            if in_bounds(ex, ey) and (ex, ey) in obstacles:
                adj_obs += 1
        val -= adj_obs * 2
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]