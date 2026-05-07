def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            r = (p[0], p[1])
            if r not in obs:
                res.append(r)
    if not res:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick a resource where we are (or can become) earlier than opponent.
    best = None
    best_key = None
    for rx, ry in res:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        if ds == 0:
            return [0, 0]
        # prioritize: earlier reach (ds-do), then shorter ds, then farther from opponent (larger do)
        key = (ds - do, ds, -do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    legal_steps = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                legal_steps.append((dx, dy))

    if not legal_steps:
        return [0, 0]

    # Choose step that maximizes relative advantage after moving.
    best_step = None
    best_step_key = None
    for dx, dy in legal_steps:
        nx, ny = sx + dx, sy + dy
        new_ds = md(nx, ny, tx, ty)
        new_do = md(ox, oy, tx, ty)
        # Prefer: keep us earlier/squeeze ds, while avoiding getting worse vs opponent.
        key = (new_ds - new_do, new_ds, -new_do, -dx, -dy)
        if best_step_key is None or key < best_step_key:
            best_step_key = key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]