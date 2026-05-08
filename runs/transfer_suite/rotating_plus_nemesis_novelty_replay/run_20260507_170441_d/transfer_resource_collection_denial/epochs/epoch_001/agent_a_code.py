def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = {tuple(p) for p in obstacles}
    candidates = [(0,0), (-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(a, b):
        dx = a[0]-b[0]
        dy = a[1]-b[1]
        return dx*dx + dy*dy

    def best_move_toward(tx, ty):
        best = None
        for dx, dy in candidates:
            nx, ny = sx+dx, sy+dy
            if not in_bounds(nx, ny) or (nx, ny) in obs_set:
                continue
            d = (nx-tx)*(nx-tx) + (ny-ty)*(ny-ty)
            # tie-break: prefer moves that improve our approach more than opponent's
            opp_d = (ox-tx)*(ox-tx) + (oy-ty)*(oy-ty)
            val = (-d, opp_d)
            if best is None or val > best[0]:
                best = (val, [dx, dy])
        return best[1] if best is not None else [0,0]

    if resources:
        best_target = None
        best_key = None
        for rx, ry in resources:
            our_d = dist2((sx, sy), (rx, ry))
            opp_d = dist2((ox, oy), (rx, ry))
            # advantage: prefer resources where we are closer (or opponent is farther)
            # also lightly prefer nearer resources overall to avoid late targets
            key = (opp_d - our_d, -(our_d), -rx, -ry)
            if best_key is None or key > best_key:
                best_key = key
                best_target = (rx, ry)
        tx, ty = best_target
        return best_move_toward(tx, ty)

    # No visible resources: drift toward center while avoiding obstacles
    cx, cy = (w-1)/2.0, (h-1)/2.0
    best = None
    for dx, dy in candidates:
        nx, ny = sx+dx, sy+dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        d = (nx-cx)*(nx-cx) + (ny-cy)*(ny-cy)
        key = (-d, dx, dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])
    return best[1] if best is not None else [0,0]