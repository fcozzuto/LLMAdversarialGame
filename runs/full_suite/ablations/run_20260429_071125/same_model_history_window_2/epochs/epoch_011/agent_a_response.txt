def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) == 2:
            obstacles.add((p[0], p[1]))
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = dx if dx >= 0 else -dx
        dy = y1 - y2; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy

    if not deltas:
        return [0, 0]

    # If no resources, drift to tighten distance to opponent while staying safe.
    if not resources:
        best_sc = -10**18; best = (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny): 
                continue
            sc = -cheb(nx, ny, ox, oy)  # approach opponent deterministically
            if sc > best_sc:
                best_sc = sc; best = (dx, dy)
        return [best[0], best[1]]

    # Choose next move that improves our relative access; if behind, deny by rushing best opponent-closer target.
    best_sc = -10**18; best = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # Safety: prefer moves that have at least one free neighboring cell (reduces dead-ends).
        free_neighbors = 0
        for ddx, ddy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
            tx, ty = nx + ddx, ny + ddy
            if inside(tx, ty):
                free_neighbors += 1

        best_target_sc = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Advantage: negative means we are closer. Convert to higher-is-better.
            adv = (od - myd)
            # Deny term: if opponent is already much closer, prioritize that resource.
            deny = 2.0 * adv - 0.35 * myd
            # Small bias to reduce absolute distance to speed captures.
            cap = 0.15 * (od - myd) - 0.06 * myd
            sc = (deny + cap) + 0.02 * (free_neighbors - 4)
            if sc > best_target_sc:
                best_target_sc = sc
        if best_target_sc > best_sc:
            best_sc = best_target_sc; best = (dx, dy)

    return [best[0], best[1]]