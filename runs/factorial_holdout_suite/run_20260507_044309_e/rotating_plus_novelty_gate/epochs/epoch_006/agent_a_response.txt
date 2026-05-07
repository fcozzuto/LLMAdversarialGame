def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set()
    for p in observation.get("obstacles", []):
        obstacles.add((p[0], p[1]))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (None, None)  # (key, move)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        # Evaluate best target from this next cell; deterministic aggregation via max key
        chosen_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # higher is better
            # Encourage finishing sooner, and slightly prefer upper-left (deterministic tie-break)
            k = (-(adv), ds, (7 - ry) * w + (7 - rx))
            if chosen_key is None or k < chosen_key:
                chosen_key = k

        if chosen_key is None:
            continue
        if best[0] is None or chosen_key < best[0]:
            best = (chosen_key, (dx, dy))

    if best[1] is None:
        return [0, 0]
    return [best[1][0], best[1][1]]