def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        d0 = dist(sx, sy, ox, oy)
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not clamp_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            dv = -dist(nx, ny, ox, oy)
            if dv > bestv:
                bestv = dv
                best = [dx, dy]
        return best

    # Target selection: prioritize resources where we are relatively closer than the opponent.
    best_t = None
    best_score = -10**18
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        rel = do - ds  # positive => we are closer than opponent
        # Encourage quick capture while also taking resources that deny opponent.
        score = 3.0 * rel - 1.0 * ds
        if score > best_score:
            best_score = score
            best_t = (rx, ry)
    tx, ty = best_t

    # Move selection: greedy toward target while avoiding obstacles; also keep some distance from opponent.
    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        ds_next = dist(nx, ny, tx, ty)
        do_next = dist(nx, ny, ox, oy)
        # If target equals current pos, stay or move minimally (dx,dy=0 likely best).
        # Balance: reduce distance to target, avoid getting too close to opponent unless it helps capture.
        v = -2.2 * ds_next + 0.25 * do_next
        # If move can potentially step onto target, strongly prefer it.
        if (nx, ny) == (tx, ty):
            v += 10**6
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best