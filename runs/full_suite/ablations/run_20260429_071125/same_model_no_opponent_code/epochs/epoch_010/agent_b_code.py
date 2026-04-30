def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def xy(v, default=None):
        if v is None:
            return default
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (int(v[0]), int(v[1]))
        if isinstance(v, dict):
            if "position" in v:
                q = v["position"]
                if isinstance(q, (list, tuple)) and len(q) >= 2:
                    return (int(q[0]), int(q[1]))
            if "x" in v and "y" in v:
                return (int(v["x"]), int(v["y"]))
        return default

    sx, sy = xy(observation.get("self_position"), (0, 0))
    ox, oy = xy(observation.get("opponent_position"), (0, 0))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        q = xy(p)
        if q is not None:
            obstacles.add((q[0], q[1]))

    resources = []
    for p in observation.get("resources", []) or []:
        q = xy(p)
        if q is not None:
            resources.append((q[0], q[1]))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        # If no visible resources, move away from opponent to avoid immediate contest
        dx = 0 if ox == sx else (1 if ox < sx else -1)
        dy = 0 if oy == sy else (1 if oy < sy else -1)
        return [dx, dy]

    # Target a resource we are more likely to secure (positive "advantage")
    best = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        adv = do - ds  # higher means we are closer than opponent
        cand = (adv, -ds, rx, ry)
        if best is None or cand > best:
            best = cand
    _, _, tx, ty = best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tie-break: fixed delta order
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_t = man(nx, ny, tx, ty)
        d_from_op = man(nx, ny, ox, oy)
        # Encourage pathing toward target and keeping distance from opponent
        # Also slightly prefer moves that reduce our nearest-resource distance
        nearest = None
        for rx, ry in resources:
            dd = man(nx, ny, rx, ry)
            if nearest is None or dd < nearest:
                nearest = dd
        val = (-d_to_t) + 0.25 * d_from_op - 0.05 * nearest
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]