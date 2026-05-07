def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        od = md(ox, oy, rx, ry)
        sd = md(sx, sy, rx, ry)
        if inb(rx, ry) and (rx, ry) in obstacles:
            continue
        # Prefer resources where we are closer; tie-break by fewer steps for us; then by position
        key = (sd - od, sd, rx, ry)
        # Small penalty if standing next to many obstacles (to avoid dead pockets)
        key = (key[0], key[1], key[2], key[3])
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    # Choose step that moves toward target and is valid
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cand.append((md(nx, ny, tx, ty), md(nx, ny, ox, oy), dx, dy))
    if not cand:
        return [0, 0]
    cand.sort()
    _, _, dx, dy = cand[0]

    # If opponent is adjacent and we are not moving toward a target better for us, step away
    if md(sx, sy, ox, oy) == 1:
        best_away = None
        for dx2, dy2 in moves:
            nx, ny = sx + dx2, sy + dy2
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            away_key = (-md(nx, ny, ox, oy), md(nx, ny, tx, ty), dx2, dy2)
            if best_away is None or away_key < best_away:
                best_away = away_key
        if best_away is not None:
            _, _, adx, ady = best_away
            return [adx, ady]
    return [dx, dy]