def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    ap = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_target():
        # Prefer resources where opponent is not much closer, but avoid ones opponent already adjacent to next.
        best = None
        bestv = -10**18
        for rx, ry in resources:
            ds = man(rx, ry, sx, sy)
            do = man(rx, ry, ox, oy)
            # If opponent can potentially grab immediately (adjacent), de-prioritize.
            opp_adj = 1 if do <= 1 else 0
            # Score: maximize advantage for us, with a small preference for closeness.
            v = (ds - do) * -10 + (1 if opp_adj == 0 else -25) + (40 - ds)
            # Secondary tie-break: deterministic by coordinates
            if v > bestv or (v == bestv and (rx, ry) < best):
                bestv = v
                best = (rx, ry)
        return best

    tx, ty = best_target()

    # Evaluate candidate moves toward target while avoiding obstacles and preventing "stupid" moves near corners.
    def move_ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not move_ok(nx, ny):
            continue
        ds_now = man(tx, ty, sx, sy)
        ds_next = man(tx, ty, nx, ny)
        do_next = man(tx, ty, ox + 0, oy + 0)  # static opponent distance estimate
        # Heuristic: prefer reducing distance; add small penalty if we allow opponent to be closer next turn to the same target.
        step_gain = ds_now - ds_next
        opp_threat = 0
        if man(tx, ty, ox, oy) <= ds_next:
            opp_threat = 1
        # Obstacle proximity penalty (encourage safer space)
        near_obs = 0
        for ddx, ddy in deltas:
            ax, ay = nx + ddx, ny + ddy
            if (ax, ay) in obstacles:
                near_obs += 1
        # Deterministic tie: prefer dx,dy order from deltas list
        sc = step_gain * 100 - (opp_threat * 30) - (near_obs * 3) - (ds_next * 2) + (1 if (nx, ny) == (tx, ty) else 0)
        if sc > best_score:
            best_score = sc
            best_move = [dx, dy]
    return best_move