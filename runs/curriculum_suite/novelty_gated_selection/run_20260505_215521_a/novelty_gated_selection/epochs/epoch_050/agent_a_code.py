def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    if w <= 0 or h <= 0:
        return [0, 0]

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    if not resources:
        return [0, 0]

    cx, cy = w // 2, h // 2
    turn = int(observation.get("turn_index", 0) or 0)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    # Choose a target: early centralization, then resource grabbing with opponent-distance bias.
    # Opponent archetype is nearest_resource, so pushing into areas it must traverse helps.
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        if turn < 6:
            tx, ty = cx, cy
        else:
            # pick best among resources and center; prefer targets that are nearer to us but farther from opponent
            # deterministic tie-break: lexicographic (tx,ty)
            best_t = (cx, cy)
            best_score = -10**18
            for rx, ry in resources + [(cx, cy)]:
                ds = man(nx, ny, rx, ry)
                do = man(ox, oy, rx, ry)
                # Encourage distancing opponent from the target while still approaching it
                score = (-ds) + 0.25 * do
                if score > best_score or (score == best_score and (rx, ry) < best_t):
                    best_score = score
                    best_t = (rx, ry)
            tx, ty = best_t

        # Evaluate move quality: progress to target + slight obstacle/engagement avoidance via opponent distance
        ds2 = man(nx, ny, tx, ty)
        do2 = man(nx, ny, ox, oy)
        # Keep stable behavior: if opponent very close, reduce pursuit by favoring distance
        val = (-ds2) + 0.08 * do2
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move