def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**18, 0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= gw or ny < 0 or ny >= gh:
            continue
        if (nx, ny) in obstacles:
            continue

        # Score the move by the best resource we can plausibly win next.
        # Prefer resources where opponent is farther, tie-break by smaller self distance.
        val = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Winning race: large weight on (od - sd). Closer to the resource wins quickly.
            # Slightly penalize large absolute distances to avoid drifting.
            v = (od - sd) * 1000 - sd * 3 - (0 if sd == 0 else 1)
            if v > val:
                val = v

        if val > best[0]:
            best = (val, dx, dy)

    return [best[1], best[2]]