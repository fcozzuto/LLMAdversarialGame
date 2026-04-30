def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs_set:
                resources.append((x, y))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    if resources:
        best = resources[0]
        best_key = None
        for tx, ty in resources:
            ds = man(sx, sy, tx, ty)
            do = man(ox, oy, tx, ty)
            beat = do - ds  # prefer targets we can reach sooner
            key = (beat, -ds, -(abs(tx - (w - 1) / 2) + abs(ty - (h - 1) / 2)))
            if best_key is None or key > best_key:
                best_key = key
                best = (tx, ty)
        tx, ty = best
        tx, ty = int(tx), int(ty)
        targets = [(tx, ty)]
    else:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        targets = [(int(round(cx)), int(round(cy)))]
        if not inside(targets[0][0], targets[0][1]):
            targets = [(sx, sy)]

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # evaluate vs best resource; if none, head to center target
        val = None
        if resources:
            # compare against each resource quickly: prefer better beat then shorter personal distance
            val = (-10**9, 10**9)
            for tx, ty in targets:
                ds = man(nx, ny, tx, ty)
                do = man(ox, oy, tx, ty)
                beat = do - ds
                key = (beat, -ds)
                if key > val:
                    val = key
        else:
            tx, ty = targets[0]
            val = (-man(nx, ny, tx, ty), 0)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]