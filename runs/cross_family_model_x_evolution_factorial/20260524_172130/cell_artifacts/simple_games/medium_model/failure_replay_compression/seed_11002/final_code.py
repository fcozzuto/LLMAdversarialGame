def choose_move(observation):
    dx = 0
    dy = 0

    obs = observation if isinstance(observation, dict) else {}
    grid_w = obs.get("grid_width", obs.get("gridW", 0))
    grid_h = obs.get("grid_height", obs.get("gridH", 0))

    self_pos = obs.get("self_position", obs.get("position", None))
    opp_pos = obs.get("opponent_position", obs.get("opponent", None))

    if isinstance(self_pos, dict):
        sx = self_pos.get("x", 0)
        sy = self_pos.get("y", 0)
    else:
        sx = 0
        sy = 0

    if isinstance(opp_pos, dict):
        ox = opp_pos.get("x", 0)
        oy = opp_pos.get("y", 0)
    else:
        ox = 0
        oy = 0

    resources = obs.get("resources", [])
    obstacles = obs.get("obstacles", [])
    remaining = obs.get("remaining_resource_count", 0)

    def step_toward(tx, ty):
        nonlocal dx, dy
        if tx > sx:
            dx = 1
        elif tx < sx:
            dx = -1
        else:
            dx = 0
        if ty > sy:
            dy = 1
        elif ty < sy:
            dy = -1
        else:
            dy = 0

    best_r = None
    best_d = None
    for r in resources:
        if not isinstance(r, dict):
            continue
        rx = r.get("x", r.get("pos", {}).get("x", 0))
        ry = r.get("y", r.get("pos", {}).get("y", 0))
        dxr = rx - sx
        dyr = ry - sy
        d = dxr*dxr + dyr*dyr
        if best_d is None or d < best_d:
            best_d = d
            best_r = (dxr, dyr, rx, ry)

    if best_r is not None:
        step_toward(best_r[2], best_r[3])
        return [dx, dy]

    if (abs(ox - sx) <= 1 and abs(oy - sy) <= 1) or (ox == sx and oy == sy):
        if ox > sx:
            dx = -1
        elif ox < sx:
            dx = 1
        else:
            dx = 0
        if oy > sy:
            dy = -1
        elif oy < sy:
            dy = 1
        else:
            dy = 0
        return [dx, dy]

    cx = max(0, min(grid_w, grid_w // 2))
    cy = max(0, min(grid_h, grid_h // 2))
    step_toward(cx, cy)
    return [dx, dy]
