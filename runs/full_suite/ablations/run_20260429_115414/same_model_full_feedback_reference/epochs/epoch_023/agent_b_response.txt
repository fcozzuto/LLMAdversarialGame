def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b, x, y):
        dx = a - x
        if dx < 0: dx = -dx
        dy = b - y
        if dy < 0: dy = -dy
        return dx + dy

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obs

    # Pick best target resource: prefer ones we're relatively closer to than opponent.
    if resources:
        best_r = None
        best_sc = -10**18
        for rx, ry in resources:
            ds = md(sx, sy, rx, ry)
            do = md(ox, oy, rx, ry)
            sc = (do - ds) * 10 - ds  # high when we deny (do > ds), then prefer nearer
            if sc > best_sc:
                best_sc = sc
                best_r = (rx, ry)
    else:
        best_r = (W // 2, H // 2)

    rx, ry = best_r
    # Choose move that minimizes our distance to target; tie-break by improving denial.
    best_m = (0, 0)
    best_pair = (10**9, -10**9)  # (self_dist, deny_score)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds2 = md(nx, ny, rx, ry)
        do2 = md(ox, oy, rx, ry)
        deny = do2 - ds2
        cand = (ds2, deny)
        if cand[0] < best_pair[0] or (cand[0] == best_pair[0] and cand[1] > best_pair[1]):
            best_pair = cand
            best_m = (dx, dy)

    if not legal(sx + best_m[0], sy + best_m[1]):
        return [0, 0]
    return [best_m[0], best_m[1]]