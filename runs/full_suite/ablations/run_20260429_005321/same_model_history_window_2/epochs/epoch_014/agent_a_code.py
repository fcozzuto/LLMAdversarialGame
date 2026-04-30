def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obst = set((int(p[0]), int(p[1])) for p in obstacles)
    res = [(int(p[0]), int(p[1])) for p in resources]

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obs_pen(x, y):
        if (x, y) in obst:
            return 10**9
        p = 0
        # Penalize adjacency to obstacles to reduce risk of getting boxed in
        for ax, ay in deltas:
            nx, ny = x + ax, y + ay
            if (nx, ny) in obst:
                p += 1
        return p

    # Choose a target: maximize opponent disadvantage while keeping us close
    if res:
        best = None
        best_key = None
        for rx, ry in res:
            dm = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Larger means better for us; tie-break deterministically by position
            key = (do - dm, -dm, -(rx + 31 * ry))
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        # No resources: move to opposite corner of opponent
        tx = 0 if ox >= w // 2 else w - 1
        ty = 0 if oy >= h // 2 else h - 1

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        pen = obs_pen(nx, ny)
        if pen >= 10**8:
            continue

        # Distance progress to target
        dm_now = cheb(sx, sy, tx, ty)
        dm_new = cheb(nx, ny, tx, ty)
        progress = dm_now - dm_new

        # Also consider whether this move improves our relative advantage to the target
        do_new = cheb(ox, oy, tx, ty)
        rel = do_new - dm_new  # higher is better for us

        # Light preference to reduce distance to closest resource (keeps collecting)
        close = 0
        if res:
            close = min(cheb(nx, ny, rx, ry) for rx, ry in res)

        score = (1000 * progress) + (10 * rel) - (2 * close) - (3 * pen) - (0 if (dx, dy) == (0, 0) else 0)
        # Deterministic tie-break: lexicographically smallest (dx,dy) among equal scores
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]