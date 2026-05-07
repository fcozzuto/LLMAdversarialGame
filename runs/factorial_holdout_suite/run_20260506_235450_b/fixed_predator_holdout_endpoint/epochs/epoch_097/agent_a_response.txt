def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def ti(v):
        try:
            return int(v)
        except:
            return 0

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = ti(sp[0]), ti(sp[1])
    ox, oy = ti(op[0]), ti(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = ti(p[0]), ti(p[1])
        elif isinstance(p, dict):
            x, y = ti(p.get("x")), ti(p.get("y"))
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = ti(r[0]), ti(r[1])
        elif isinstance(r, dict) and "x" in r and "y" in r:
            x, y = ti(r.get("x")), ti(r.get("y"))
        else:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            res.append((x, y))
    if not res:
        return [0, 0]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    my_step_options = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                my_step_options.append((dx, dy, nx, ny))
    if not my_step_options:
        return [0, 0]

    # Prefer resources where we are (strictly) not behind.
    best_target = None
    best_key = None
    behind_targets = []
    for (rx, ry) in res:
        md = dist(rx, ry, sx, sy)
        od = dist(rx, ry, ox, oy)
        if md <= od - 1:
            key = (md, -od, rx, ry)  # closest and deny far
            if best_key is None or key < best_key:
                best_key = key
                best_target = (rx, ry)
        else:
            behind_targets.append((rx, ry, md, od))

    if best_target is not None:
        tx, ty = best_target
    else:
        # If we can't beat opponent, denial: chase their closest remaining resource.
        # (Resource_denier tends to head for what it can take; intercept that.)
        cx, cy, _, _ = min(behind_targets, key=lambda t: (t[3], t[2], t[0], t[1]))
        tx, ty = cx, cy

    # Choose the move that minimizes our distance to chosen target; tie-break with opponent distance.
    chosen = None
    chosen_key = None
    for dx, dy, nx, ny in my_step_options:
        md = dist(tx, ty, nx, ny)
        od = dist(tx, ty, ox, oy)
        # If we're targeting their resource, also reduce their distance (adversarial tie-break).
        opp_my = dist(ox, oy, nx, ny)
        key = (md, abs(od - md), opp_my, dx, dy)
        if chosen_key is None or key < chosen_key:
            chosen_key = key
            chosen = (dx, dy)
    return [chosen[0], chosen[1]]