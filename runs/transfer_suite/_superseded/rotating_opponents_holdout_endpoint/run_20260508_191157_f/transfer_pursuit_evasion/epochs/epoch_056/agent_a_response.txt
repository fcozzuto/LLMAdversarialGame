def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("evade" in role) or ("evasion" in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def corners():
        return [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    if is_evader:
        # Flee toward the farthest corner (among corners), while maximizing distance from pursuer.
        best_corner = None
        best_corner_dist = -1
        for cx, cy in corners():
            d = cheb(cx, cy, ox, oy)  # far from opponent
            if d > best_corner_dist:
                best_corner_dist = d
                best_corner = (cx, cy)
        tx, ty = best_corner
        want_dist = 1  # maximize
    else:
        # Pursuer: chase to minimize distance, with a slight preference for moving "past" the opponent.
        tx, ty = ox, oy
        # If aligned, push past in the same direction from self to opponent.
        dx_dir = 0 if ox == sx else (1 if ox > sx else -1)
        dy_dir = 0 if oy == sy else (1 if oy > sy else -1)
        px, py = sx + dx_dir, sy + dy_dir
        if ok(px, py):
            tx, ty = px, py
        want_dist = -1  # minimize

    # Deterministic tie-break: fixed ordering by (score desc, x, y) depending on want_dist.
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist_op = cheb(nx, ny, ox, oy)
        dist_t = cheb(nx, ny, tx, ty)

        # Obstacle-aware bias: prefer moves that have more free neighbors (avoid dead ends).
        free_neighbors = 0
        for adx, ady in moves:
            ax, ay = nx + adx, ny + ady
            if ok(ax, ay):
                free_neighbors += 1

        # Score: for evader maximize distance from opponent; for pursuer minimize it.
        # Add small terms to break ties toward progress and avoid dead ends.
        if want_dist == 1:
            score = dist_op * 100 + dist_t * 2 + free_neighbors
            key = (-score, nx, ny)  # we want highest score
        else:
            score = dist_op * 100 - dist_t * 2 + free_neighbors  # dist_t smaller is better for pursuer
            key = (-score, nx, ny)  # we want highest score

        if best is None or key < best_key:
            best = (dx, dy)
            best_key = key

    if best is None:
        return [0, 0]
    return [best[0], best[1]]