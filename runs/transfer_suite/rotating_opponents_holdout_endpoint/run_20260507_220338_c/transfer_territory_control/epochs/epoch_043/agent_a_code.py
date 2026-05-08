def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    ox, oy = int(ox), int(oy)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs_set = set()
    for p in obstacles:
        try:
            obs_set.add((int(p[0]), int(p[1])))
        except:
            pass

    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    for p in unclaimed:
        try:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obs_set and (x, y) != (sx, sy):
                targets.append((x, y))
        except:
            pass

    if not targets:
        resources = observation.get("resources") or []
        for p in resources:
            try:
                x, y = int(p[0]), int(p[1])
                if (x, y) not in obs_set and (x, y) != (sx, sy):
                    targets.append((x, y))
            except:
                pass

    if not targets:
        targets = [(ox, oy)]

    best = None
    best_d = None
    for tx, ty in targets:
        d = (tx - sx) * (tx - sx) + (ty - sy) * (ty - sy)
        if best_d is None or d < best_d or (d == best_d and (tx, ty) < best):
            best_d = d
            best = (tx, ty)
    tx, ty = best if best is not None else (ox, oy)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    move_order = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        dist = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        gain = 0
        if targets:
            gain = best_d - dist
        tie = (dx, dy)
        move_order.append((dist, -gain, tie, [dx, dy]))
    if not move_order:
        return [0, 0]
    move_order.sort()
    return move_order[0][3]