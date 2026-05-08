def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def pos_of(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", v.get("xy", None)))
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return int(p[0]), int(p[1])
        return None

    sp = pos_of(observation.get("self_position", None))
    if sp is None:
        sp = (0, 0)
    op = pos_of(observation.get("opponent_position", None))
    if op is None:
        op = sp
    sx, sy = sp
    ox, oy = op

    obs = set()
    for o in observation.get("obstacles", []) or []:
        p = pos_of(o)
        if p is None:
            continue
        x, y = p
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        p = pos_of(r)
        if p is None:
            continue
        x, y = p
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best = None
    best_key = None

    # Heuristic: prefer moves that reduce our distance to the closest resource;
    # break ties by increasing distance to opponent; deterministic tie-breaking.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if resources:
            md = None
            for (rx, ry) in resources:
                d = abs(nx - rx) + abs(ny - ry)
                if md is None or d < md:
                    md = d
        else:
            md = 0
        od = abs(nx - ox) + abs(ny - oy)
        key = (md, -od, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]