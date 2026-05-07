def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    # Pick target resource that we can secure best relative to opponent (lower opponent distance advantage).
    best = None
    best_key = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # want us closer than opponent (sd-od small), but also prefer closer absolute.
        key = (sd - od, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_eval = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        self_t = md(nx, ny, tx, ty)
        opp_t = md(nx, ny, tx, ty)
        # Evaluate each move by: improve relative distance to target and immediate "capture" if on a resource.
        on_res = 1 if any(nx == rx and ny == ry for rx, ry in resources) else 0
        # Deny logic for opponent: minimize max of our distance to targets we can reach soon vs opponent.
        # Cheap approximation: look at nearest 3 resources by our distance.
        nearest = []
        for rx, ry in resources:
            nearest.append((md(nx, ny, rx, ry), md(ox, oy, rx, ry), rx, ry))
        nearest.sort()
        # compute a compact relative objective
        rel = 0
        take = nearest[:3]
        for sd, od, rx, ry in take:
            # prefer resources where we beat opponent; penalize where opponent beats us.
            rel += (sd - od)
            # slight preference for closer resources
            rel += 0.01 * sd

        # Prefer being closer to target, and capturing resources.
        self_adv = (self_t - md(ox, oy, tx, ty))
        # Lower is better; construct deterministic tuple.
        eval_key = (
            0 if on_res else 1,
            self_adv,
            rel,
            self_t,
            dx, dy
        )
        if best_eval is None or eval_key < best_eval:
            best_eval = eval_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]