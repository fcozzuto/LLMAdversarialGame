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

    # Pick best target with a stronger "beat opponent" bias than just closeness.
    best_t = None
    best_sc = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer: resources we can take first; then maximize lead; then prefer reducing own distance.
        sc = (do - ds) * 1000 - ds * 3
        # Slightly bias toward cells away from opponent (helps vs row/line sweepers).
        sc += (cheb(ox, oy, rx, ry) - cheb(sx, sy, rx, ry)) * 2
        if sc > best_sc:
            best_sc = sc
            best_t = (rx, ry)

    tx, ty = best_t
    if cheb(sx, sy, tx, ty) == 0:
        return [0, 0]

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh):
            continue
        if (nx, ny) in obstacles:
            continue
        nds = cheb(nx, ny, tx, ty)
        ndo = cheb(ox, oy, tx, ty)
        # Move selection: go closer to target; keep/extend advantage; avoid stepping into losing contests.
        val = (ndo - nds) * 1000 - nds * 5
        # If contest tight, prefer increasing distance from opponent.
        val += cheb(nx, ny, ox, oy) * 2 - cheb(sx, sy, ox, oy) * 1
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move