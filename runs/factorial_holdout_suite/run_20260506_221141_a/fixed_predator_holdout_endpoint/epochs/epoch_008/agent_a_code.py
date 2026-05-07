def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    if not resources:
        return [0, 0]
    obs = {(int(a), int(b)) for a, b in obstacles}

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Select a target resource deterministically.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = md(x, y, rx, ry)
        od = md(ox, oy, rx, ry)
        key = (-(od - sd), sd, rx, ry)  # maximize (od-sd): we are relatively closer
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # If opponent is at least as close, switch to contesting: pick a target where
    # our relative advantage is smallest (resource_denier behavior).
    if md(ox, oy, tx, ty) <= md(x, y, tx, ty) and len(resources) > 1:
        best_key = None
        best = None
        for rx, ry in resources:
            sd = md(x, y, rx, ry)
            od = md(ox, oy, rx, ry)
            key = (sd - od, sd, rx, ry)  # minimize our advantage
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    opp_close = md(ox, oy, tx, ty) <= md(x, y, tx, ty)

    # Choose a legal one-step move that optimizes approach to the target and contest logic.
    best_move = [0, 0]
    best_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obs:
                continue
            nsd = md(nx, ny, tx, ty)
            nod = md(ox, oy, tx, ty)  # opponent doesn't move this turn in our evaluation
            if opp_close:
                val = (nsd - nod, nsd, -dx, -dy)  # when contesting, reduce opp-snd gap from our perspective
            else:
                val = (-(nod - nsd), nsd, -dx, -dy)  # maximize relative advantage; tie-break closer
            if best_val is None or val < best_val:
                best_val = val
                best_move = [dx, dy]

    return best_move