def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_r = None
    best_key = None
    for (rx, ry) in resources:
        if not valid(rx, ry):
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach first; then prioritize closer; finally deterministic tie-break.
        key = (do < ds, do - ds, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_r

    best_step = (0, 0)
    best_step_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds = cheb(nx, ny, tx, ty)
        # If opponent is racing the target, bias toward shortening our advantage.
        do = cheb(ox, oy, tx, ty)
        # Also gently discourage stepping away from all resources.
        min_res = None
        for (rx, ry) in resources[: min(12, len(resources))]:
            if valid(rx, ry):
                d = cheb(nx, ny, rx, ry)
                if min_res is None or d < min_res:
                    min_res = d
        if min_res is None:
            min_res = cheb(nx, ny, tx, ty)
        step_key = (do < ds, do - ds, ds, min_res, dx, dy, nx, ny)
        if best_step_key is None or step_key < best_step_key:
            best_step_key = step_key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]