def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(s[0]), int(s[1]), int(o[0]), int(o[1])

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

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Prefer resources where we are closer (Chebyshev), else still move toward best overall.
    best_r = None
    best_key = None
    for rx, ry in resources:
        myd = dist((sx, sy), (rx, ry))
        opd = dist((ox, oy), (rx, ry))
        adv = opd - myd
        key = (adv, -myd, -(rx + 3 * ry))  # deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r

    # Evaluate legal step deltas (including stay) by progress toward target,
    # with a strong penalty for stepping into obstacles or leaving grid.
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_step = (0, 0)
    best_step_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        myd_next = dist((nx, ny), (tx, ty))
        myd_now = dist((sx, sy), (tx, ty))
        progress = myd_now - myd_next

        # Additional tie-break: if we can't beat opponent on this target, try to reduce opponent pressure
        # by also moving to reduce max-distance to target from opponent.
        opd_next = dist((ox, oy), (tx, ty))
        key = (progress, -myd_next, adv if (dist((ox, oy), (tx, ty)) - dist((nx, ny), (tx, ty))) >= 0 else -myd_next,
               nx - 0.0 * ny, -(dx * 10 + dy))
        if best_step_key is None or key > best_step_key:
            best_step_key = key
            best_step = (dx, dy)

    dx, dy = best_step
    return [int(dx), int(dy)]