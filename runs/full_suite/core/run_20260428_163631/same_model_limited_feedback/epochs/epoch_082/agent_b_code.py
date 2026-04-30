def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs_set = set((p[0], p[1]) for p in obstacles)
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    # Target: nearest remaining resource (Chebyshev distance)
    best = None
    bx, by = None, None
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        d = max(abs(rx - x), abs(ry - y))
        if best is None or d < best or (d == best and (rx, ry) < (bx, by)):
            best = d
            bx, by = rx, ry

    # Prefer moves that reduce distance to target while avoiding obstacles
    dxs = [-1, 0, 1]
    dys = [-1, 0, 1]
    candidates = []
    for dx in dxs:
        for dy in dys:
            nx, ny = x + dx, y + dy
            if (nx < 0 or nx >= w or ny < 0 or ny >= h) or (nx, ny) in obs_set:
                continue
            dist = max(abs(bx - nx), abs(by - ny))
            # Small tie-break: also consider opponent distance to reduce being blocked
            opp = max(abs(ox - nx), abs(oy - ny))
            candidates.append((dist, -opp, dx, dy))
    # Deterministic best: min dist, then max opp distance (negative), then lexical by dx,dy
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
    return [candidates[0][2], candidates[0][3]]