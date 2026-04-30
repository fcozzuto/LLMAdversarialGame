def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def free(x, y):
        return (x, y) not in obstacles

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None

    targets = resources if resources else [(ox, oy)]
    for dx, dy in dirs:
        nx, ny = clamp(sx + dx, sy + dy)
        if not free(nx, ny):
            continue
        # Score: prefer resources (or opponent if no resources), avoid obstacles, prefer closeness to opponent if resources absent
        if resources:
            tx, ty = min(targets, key=lambda p: (p[0]-nx)*(p[0]-nx) + (p[1]-ny)*(p[1]-ny))
            tdist = abs(nx - tx) + abs(ny - ty)
            score = -tdist
        else:
            odist = abs(nx - ox) + abs(ny - oy)
            score = -odist

        for ax, ay in obstacles:
            dd = abs(nx - ax) + abs(ny - ay)
            score += 1.0 / (dd + 1)

        if best is None or score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    if best is None:
        for dx, dy in dirs:
            nx, ny = clamp(sx + dx, sy + dy)
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best[1], best[2]]