def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    if not resources:
        return [0, 0]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def reach_step_cost(nx, ny, tx, ty):
        # Prefer progress to target; slight penalty for being close to obstacles-adjacent
        return man(nx, ny, tx, ty)

    # Choose target resource: prioritize being closer than opponent; break ties by closeness.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        lead = od - sd  # positive => we are closer
        # Also prefer resources that are not immediately "behind" the opponent (smaller od).
        key = (lead > 0, lead, -sd, -od, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_step = (0, 0)
    best_step_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        sd2 = man(nx, ny, tx, ty)
        od_curr = man(ox, oy, tx, ty)

        # If we are already closer, keep pressure: reduce opponent distance by minimizing our own retreat
        # relative to staying in the line.
        # Also add small term to avoid stepping away if we can capture soon.
        progress = (man(sx, sy, tx, ty) - sd2)
        # Risk term: discourage moves that move us toward cells adjacent to obstacles (local navigation).
        risk = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    risk += 1

        key = (
            sd2,
            -progress,
            -risk,
            abs((od_curr - man(nx, ny, tx, ty))),
            -nx, -ny
        )
        if best_step_key is None or key < best_step_key:
            best_step_key = key
            best_step = (dx, dy)

    dx, dy = best_step
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [int(dx), int(dy)]