def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if resources:
            # Prefer moves that get us closer to a resource and keep away from opponent access.
            score = None
            for rx, ry in resources:
                ds = (nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)
                do = (ox - rx) * (ox - rx) + (oy - ry) * (oy - ry)
                val = ds - 0.6 * do
                if score is None or val < score:
                    score = val
            cur = score
        else:
            # No resources: move to increase distance from opponent.
            cur = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if best_score is None or cur > best_score or (cur == best_score and (dx, dy) < best):
            best_score = cur
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]