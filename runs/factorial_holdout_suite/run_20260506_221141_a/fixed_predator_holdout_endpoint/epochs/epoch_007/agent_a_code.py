def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = observation.get("obstacles", [])
    obs = {(a, b) for a, b in obstacles}

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Prefer resources where we are closer (likely reach first), then nearer ones.
    best_t = None
    best_key = None
    for rx, ry in resources:
        sd = md(x, y, rx, ry)
        od = md(ox, oy, rx, ry)
        key = (-(od - sd), sd, rx, ry)  # maximize (od-sd) => minimize negative
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)
    tx, ty = best_t

    # If opponent is already very close to the target, try contesting nearest resource for them.
    opp_close = md(ox, oy, tx, ty) <= md(x, y, tx, ty)
    if opp_close and len(resources) > 1:
        worst_for_us = None
        worst_key = None
        for rx, ry in resources:
            sd = md(x, y, rx, ry)
            od = md(ox, oy, rx, ry)
            # Choose where opponent is relatively closer to contest; minimize our advantage.
            key = (sd - od, sd, rx, ry)
            if worst_key is None or key < worst_key:
                worst_key = key
                worst_for_us = (rx, ry)
        if worst_for_us is not None:
            tx, ty = worst_for_us

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        sd_new = md(nx, ny, tx, ty)
        sd_curr = md(x, y, tx, ty)
        od_new = md(nx, ny, ox, oy)  # proxy for keeping opponent far from us
        # Main: reduce distance to target; Secondary: improve our lead vs opponent on that target.
        # Tie-break deterministically toward smaller (dx,dy) ordering.
        lead_new = md(ox, oy, tx, ty) - sd_new
        val = (-(lead_new), sd_new, -od_new, sd_curr - sd_new, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_mv = (dx, dy)

    dx, dy = best_mv
    return [int(dx), int(dy)]