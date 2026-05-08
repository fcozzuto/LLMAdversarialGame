def choose_move(observation):
    def to_xy(v):
        if isinstance(v, (list, tuple)) and len(v) == 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) == 2:
                return int(p[0]), int(p[1])
        return None

    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = to_xy(observation.get("self_position", [0, 0])) or (0, 0)
    op = to_xy(observation.get("opponent_position", [0, 0])) or (0, 0)
    sx, sy = sp
    ox, oy = op

    obs = set()
    for o in observation.get("obstacles", []) or []:
        t = to_xy(o)
        if t:
            x, y = t
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        t = to_xy(r)
        if t:
            x, y = t
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_target():
        if not resources:
            return None
        best = None
        for cell in resources:
            sd = man((sx, sy), cell)
            od = man((ox, oy), cell)
            # Prefer resources where we are closer than opponent; otherwise still contest.
            margin = od - sd
            score = (margin, -sd, -cell[0], -cell[1])
            if best is None or score > best[0]:
                best = (score, cell)
        return best[1]

    target = best_target()
    if target is None:
        return [0, 0]

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (None, None)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        sd = man((nx, ny), target)
        od = man((ox, oy), target)
        # Greedy toward target but also improve contest margin; prefer closer and safer.
        val = (od - sd, -sd, -abs(ox - nx) - abs(oy - ny), -dx, -dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0] if best_move[0] is not None else 0), int(best_move[1] if best_move[1] is not None else 0)]