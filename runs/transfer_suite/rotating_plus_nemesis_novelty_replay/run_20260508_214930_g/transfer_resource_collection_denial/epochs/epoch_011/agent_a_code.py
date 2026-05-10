def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Choose resource likely to be captured first by maximizing (opp_dist - my_dist).
    best = None
    for rx, ry in resources:
        d0 = cheb(sx, sy, rx, ry)
        d1 = cheb(ox, oy, rx, ry)
        # Prefer earlier by being smaller dist; also prefer central-ish when tied.
        key = (d1 - d0, -(rx + ry), -d0, -cheb(rx, ry, w // 2, h // 2))
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_val = None

    # One-step evaluation: move that improves capture race, avoids obstacles, and blocks opponent line slightly.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        my_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        race = opp_d - my_d

        # Small repulsion from obstacles and desire to approach nearest resource overall.
        near_res = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < near_res:
                near_res = d

        # Bonus if we reduce our distance compared to staying still.
        stay_d = cheb(sx, sy, tx, ty)
        progress = stay_d - my_d

        # Mild "intercept": also consider the closest resource distance to opponent after their move (approx).
        opp_near = 10**9
        for rx, ry in resources:
            d = cheb(ox, oy, rx, ry)
            if d < opp_near:
                opp_near = d

        # Penalty if we move closer to opponent than we must (encourage race advantage, not dogfights).
        my_to_opp = cheb(nx, ny, ox, oy)
        stay_to_opp = cheb(sx, sy, ox, oy)
        closeness = stay_to_opp - my_to_opp  # positive if we separate

        val = (race, progress, -my_d, -near_res, closeness, -opp_near, -(nx + ny))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    # If all moves filtered out (unlikely), allow stay.
    return [best_move[0], best_move[1]]