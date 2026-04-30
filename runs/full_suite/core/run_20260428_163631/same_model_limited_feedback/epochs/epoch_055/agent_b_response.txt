def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(0,0), (1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources, just drift toward opponent to contest space.
    if not resources:
        tx, ty = ox, oy
        best = (0, 0, -10**9)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h: continue
            if (nx, ny) in obstacles: continue
            sc = -cheb(nx, ny, tx, ty)
            if sc > best[2] or (sc == best[2] and (dx, dy) < (best[0], best[1])):
                best = (dx, dy, sc)
        return [best[0], best[1]]

    # Switch to contested-resource targeting: prefer resources where we have a real distance edge over opponent.
    best_t = None
    best_score = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Primary: maximize advantage (opponent farther). Secondary: keep it reasonably close.
        sc = (do - ds) * 100 - ds * 3
        # Mild bias toward not-too-far resources to reduce wandering.
        sc += (8 - min(ds, 8)) * 0.5
        if sc > best_score:
            best_score = sc
            best_t = (rx, ry)

    tx, ty = best_t

    # Choose move that best reduces distance to target, while avoiding obstacles.
    best = (0, 0, -10**18)
    curd = cheb(sx, sy, tx, ty)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h: continue
        if (nx, ny) in obstacles: continue
        nd = cheb(nx, ny, tx, ty)
        # Prefer getting closer; if equal, prefer breaking ties toward lower opponent distance (contesting).
        oppd = cheb(ox, oy, nx, ny)
        sc = -(nd - curd) * 100 - nd * 2 - oppd * 0.01
        if sc > best[2] or (sc == best[2] and (dx, dy) < (best[0], best[1])):
            best = (dx, dy, sc)

    return [best[0], best[1]]