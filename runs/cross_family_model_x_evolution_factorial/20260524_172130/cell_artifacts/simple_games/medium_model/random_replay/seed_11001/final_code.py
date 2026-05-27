def choose_move(observation):
    grid_w = observation.get('grid_width', 0)
    grid_h = observation.get('grid_height', 0)
    sx, sy = observation.get('self_position', [0, 0])
    obstacles = observation.get('obstacles', [])
    resources = observation.get('resources', [])
    rem = observation.get('remaining_resource_count', 0)

    dx = 0
    dy = 0

    obs_set = set()
    for o in obstacles or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obs_set.add((o[0], o[1]))
        elif isinstance(o, dict):
            ox = o.get('x', 0)
            oy = o.get('y', 0)
            obs_set.add((ox, oy))

    if isinstance(resources, list) and resources:
        best = None
        best_dist = float('inf')
        for r in resources:
            if isinstance(r, dict):
                rx = r.get('pos', [0, 0])[0]
                ry = r.get('pos', [0, 0])[1]
            else:
                rx = r[0] if len(r) > 0 else 0
                ry = r[1] if len(r) > 1 else 0
            dxr = sx - rx
            dyr = sy - ry
            dist = dxr * dxr + dyr * dyr
            if dist < best_dist:
                best_dist = dist
                best = (rx, ry)
        if best is not None:
            if best[0] > sx:
                dx = 1
            elif best[0] < sx:
                dx = -1
            if best[1] > sy:
                dy = 1
            elif best[1] < sy:
                dy = -1

    nx, ny = sx + dx, sy + dy
    blocked = (nx, ny) in obs_set or not (0 <= nx < grid_w and 0 <= ny < grid_h)

    if blocked:
        fallback_dx, fallback_dy = 0, 0
        if dx != 0:
            if (sx, sy + 1) not in obs_set and 0 <= sy + 1 < grid_h:
                fallback_dx, fallback_dy = 0, 1
            elif (sx, sy - 1) not in obs_set and 0 <= sy - 1 < grid_h:
                fallback_dx, fallback_dy = 0, -1
        if dx == 0 and dy != 0:
            if (sx + 1, sy) not in obs_set and 0 <= sx + 1 < grid_w:
                fallback_dx, fallback_dy = 1, 0
            elif (sx - 1, sy) not in obs_set and 0 <= sx - 1 < grid_w:
                fallback_dx, fallback_dy = -1, 0

        if (fallback_dx, fallback_dy) != (0, 0):
            dx, dy = fallback_dx, fallback_dy
        else:
            dx, dy = 0, 0

    return [dx, dy]
