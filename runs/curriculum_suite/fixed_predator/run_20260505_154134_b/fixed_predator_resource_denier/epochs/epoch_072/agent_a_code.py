def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = -(cheb(nx, ny, tx, ty)) + 0.05 * cheb(nx, ny, ox, oy)
            t = cheb(nx, ny, tx, ty)
            key = (v, -t, -dx, -dy)
            if best is None or key > best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    best_move = [0, 0]
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Choose a resource to pursue, but score the move by "how denial-favorable it is":
        # prefer resources where our distance is smaller than opponent's, and where we can get close quickly.
        best_res = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Advantage to us, with a quick-commit bias to reduce our distance.
            adv = od - sd
            key = (adv, -sd, -cheb(ox, oy, nx, ny), rx, ry)
            if best_res is None or key > best_res:
                best_res = key

        adv, neg_sd, _, rx, ry = best_res
        sd = -neg_sd

        # Additional shaping: avoid moves that worsen our nearest-resource distance.
        cur_near = min(cheb(sx, sy, r[0], r[1]) for r in resources)
        new_near = min(cheb(nx, ny, r[0], r[1]) for r in resources)
        progress = cur_near - new_near

        # Small tie-breaker to steer toward that chosen resource more directly.
        steer = -cheb(nx, ny, rx, ry)

        # Deterministic total key
        key = (adv, progress, steer, -sd, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move