def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = set()
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                res.add((x, y))
        elif isinstance(r, dict):
            pos = r.get("position", r.get("pos", None))
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                x, y = int(pos[0]), int(pos[1])
                if 0 <= x < w and 0 <= y < h:
                    res.add((x, y))

    if (sx, sy) in res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = abs(bx - ax); dy = abs(by - ay)
        return dx if dx > dy else dy

    best_move = [0, 0]
    best_key = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obs:
                continue

            # Evaluate best resource from the hypothetical next position.
            local_best = None
            for tx, ty in res:
                if (tx, ty) in obs:
                    continue
                sd = cheb(nx, ny, tx, ty)
                od = cheb(ox, oy, tx, ty)
                # Prefer winning races; break ties by closer to the target.
                key = (od - sd, -sd, -(abs(tx - nx) + abs(ty - ny)))
                if local_best is None or key > local_best[0]:
                    local_best = (key, (tx, ty), sd, od)

            if local_best is None:
                # No reachable resources (shouldn't happen often).
                key = (-10**9, 0, 0)
            else:
                key = local_best[0]

            if best_key is None or key > best_key:
                best_key = key
                best_move = [dx, dy]

    return best_move