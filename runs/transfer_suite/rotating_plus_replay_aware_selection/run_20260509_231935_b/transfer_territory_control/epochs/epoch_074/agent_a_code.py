def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            q = p.get("position") or p.get("cell")
            if isinstance(q, (list, tuple)) and len(q) == 2:
                obs.add((int(q[0]), int(q[1])))

    def extract_cell(item):
        if isinstance(item, (list, tuple)) and len(item) == 2:
            return (int(item[0]), int(item[1]))
        if isinstance(item, dict):
            q = item.get("position") or item.get("cell")
            if isinstance(q, (list, tuple)) and len(q) == 2:
                return (int(q[0]), int(q[1]))
        return None

    resources = observation.get("resources") or []
    targets = []
    for r in resources:
        c = extract_cell(r)
        if c is not None:
            x, y = c
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                targets.append((x, y))

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax + ay

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_score = None

    if targets:
        tx, ty = min(targets, key=lambda p: man(sx, sy, p[0], p[1]))
        aim_x, aim_y = tx, ty
    else:
        aim_x, aim_y = ox, oy

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d_aim = man(nx, ny, aim_x, aim_y)
        d_opp = man(nx, ny, ox, oy)
        score = (-d_aim, d_opp, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best