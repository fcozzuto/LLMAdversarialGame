def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    valid = []
    for r in resources:
        x, y = r[0], r[1]
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            valid.append((x, y))
    if not valid:
        return [0, 0]

    tr = observation.get("turns_remaining", 0)
    remaining = observation.get("remaining_resource_count", len(valid))
    few = (tr <= 6) or (remaining <= 3)

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0:
            ax = -ax
        if ay < 0:
            ay = -ay
        return ax + ay

    best = None
    best_val = None
    for rx, ry in valid:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        lead = od - sd  # positive means we are closer (better)
        # Value shaped to prioritize leads, then proximity, stronger when few left
        v = lead * 3.0 - sd * (0.35 if not few else 0.55)
        v += (2.2 if sd <= 1 else 0.0)
        if few:
            v += 4.0 / (sd + 1.0)
        # Deterministic tie-break toward center
        cx, cy = w // 2, h // 2
        center = - (man(rx, ry, cx, cy) * 0.01)
        v += center
        if best_val is None or v > best_val:
            best_val = v
            best = (rx, ry)

    tx, ty = best

    # Choose actual one-step delta minimizing distance to chosen target, avoiding obstacles.
    options = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_step = (0, 0)
    best_d = None
    for dx, dy in options:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = man(nx, ny, tx, ty)
        # Tie-break: prefer moves that keep lead vs opponent (local)
        nd_opp = man(ox, oy, tx, ty) - d
        key = (d, -nd_opp)
        if best_d is None or key < best_d:
            best_d = key
            best_step = (dx, dy)

    dx, dy = best_step
    return [int(dx), int(dy)]