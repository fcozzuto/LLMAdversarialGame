def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose move that maximizes our "distance advantage" to the best contested resource after one step.
    best_delta = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Prefer resources where we can be closer than opponent; also discourage giving opponent closer access.
        local_best = -10**18
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            adv = od - sd  # higher is better (we are closer than opponent)
            # Tie-breakers: closer target for us, then safer against opponent proximity overall.
            val = (adv * 1000) - sd + (od - sd) * 0.1
            local_best = val if val > local_best else local_best

        # Small additional bias toward reducing our distance to current best compared to staying.
        if local_best > best_val + 1e-9:
            best_val = local_best
            best_delta = (dx, dy)
        elif abs(local_best - best_val) <= 1e-9:
            # Deterministic tie-break: prefer straight/diagonal order by dirs list, already deterministic due to iteration.
            pass

    return [int(best_delta[0]), int(best_delta[1])]