def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            resources.append((int(r[0]), int(r[1])))
        except Exception:
            pass

    def cheb(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x if x > y else y

    if not resources:
        tx, ty = (0, 0) if ((ox + oy) & 1) == 0 else (w - 1, h - 1)
    else:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer states where we are closer than opponent; if tied, reduce our distance.
            lead = do - ds
            key = (lead, -ds, -(abs(rx - ox) + abs(ry - oy)), -(abs(rx - sx) + abs(ry - sy)))
            if best is None or key > best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = None
    best_key = None
    target_set = set(resources)  # for fast adjacent/resource-on-tile check

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        ds2 = cheb(nx, ny, tx, ty)
        on_resource = 1 if (nx, ny) in target_set else 0
        # If we can't secure lead, still move to reduce our distance and avoid "stalling" near obstacles.
        neigh_obs = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ax, ay = nx + ddx, ny + ddy
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obstacles:
                    neigh_obs += 1
        key = (on_resource, -ds2, -neigh_obs, -cheb(ox, oy, tx, ty))
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]