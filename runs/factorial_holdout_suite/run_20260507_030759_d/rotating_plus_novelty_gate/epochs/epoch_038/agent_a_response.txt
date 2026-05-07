def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res_set = set(tuple(r) for r in resources)
    if (sx, sy) in res_set and (sx, sy) not in obstacles:
        return [0, 0]

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        # Drift toward farthest corner from opponent while staying roughly safe
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        bestv = None
        for cx, cy in corners:
            v = (abs(cx - ox) - abs(sx - ox) - (abs(cy - oy) - abs(sy - oy)),
                 -(abs(cx - sx) + abs(cy - sy)))
            if bestv is None or v > bestv:
                bestv = v
                best = (cx, cy)
        tx, ty = best
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if (sx + dx, sy + dy) in obstacles or not inb(sx + dx, sy + dy):
            return [0, 0]
        return [dx, dy]

    # Pick a target that we can reach sooner than opponent; break ties by being closer.
    best_t = None
    best_key = None
    for rx, ry in resources:
        ds = max(0, abs(rx - sx) + abs(ry - sy))
        do = max(0, abs(rx - ox) + abs(ry - oy))
        # We want (do - ds) large; then -ds small distance to secure; then deterministic by coords.
        key = (do - ds, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)
    tx, ty = best_t

    # Score each move using: progress to target, relative gain vs opponent, and slight repulsion from obstacles.
    def obstacle_repulse(nx, ny):
        # small penalty if adjacent to obstacle to avoid bumps; deterministic and cheap
        p = 0
        for ax, ay in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            if (nx + ax, ny + ay) in obstacles:
                p += 1
        return p

    best_move = None
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        ds_now = abs(tx - sx) + abs(ty - sy)
        ds_next = abs(tx - nx) + abs(ty - ny)
        do_now = abs(tx - ox) + abs(ty - oy)
        do_next = abs(tx - ox - dx) + abs(ty - oy - dy)  # approximate opponent response to our move direction

        rel_gain = (do_now - ds_now) - (do_next - ds_next)
        # Lower score obstacle repulse; higher progress; also prefer not losing relative advantage.
        score = (ds_now - ds_next, rel_gain, -obstacle_repulse(nx, ny), -abs(ox - nx) - abs(oy - ny), -nx, -ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]