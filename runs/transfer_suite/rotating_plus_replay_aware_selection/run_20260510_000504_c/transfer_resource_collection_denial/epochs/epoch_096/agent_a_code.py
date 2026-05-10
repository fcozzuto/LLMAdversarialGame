def choose_move(observation):
    def xy_from(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            if "position" in v:
                p = v["position"]
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    return int(p[0]), int(p[1])
            if "x" in v and "y" in v:
                return int(v["x"]), int(v["y"])
        return None

    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = xy_from(observation.get("self_position") or [0, 0]) or (0, 0)
    op = xy_from(observation.get("opponent_position") or [0, 0]) or (0, 0)
    sx, sy = sp
    ox, oy = op

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        q = xy_from(p)
        if q:
            x, y = q
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    targets = []
    for r in resources:
        q = xy_from(r)
        if q:
            x, y = q
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                targets.append((x, y))

    if not targets:
        return [0, 0]

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        md = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
        # Prefer moving toward resources; break ties deterministically by opponent distance and direction.
        ok = min(abs(nx - ox) + abs(ny - oy), 10**9)
        key = (md, -ok, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]