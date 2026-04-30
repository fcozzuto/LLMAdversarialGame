def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))
    resources = sorted(set(resources))

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    # If no visible resources, step toward opponent's side but stay safe
    if not resources:
        tx = (W - 1) - ox
        ty = (H - 1) - oy
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            v = -d
            if v > best_val:
                best_val = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Evaluate by best "win" resource where we are closer than opponent
        v = 0.0
        min_self = 10**9
        min_opp = 10**9
        best_margin = -10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if ds < min_self: min_self = ds
            if do < min_opp: min_opp = do
            margin = do - ds  # positive if we are closer
            if margin > best_margin:
                best_margin = margin
                v = margin * 100.0 - ds  # strongly prefer resources we can beat
        # Penalize if staying gives no improvement when we're behind
        if best_margin < 0:
            v -= (min_opp - min_self) * 10.0
        # Subtle preference for reducing distance to closest resource
        v -= min_self * 0.5
        # Deterministic tie-break: prefer lexicographically smaller (dx,dy) among equals
        if v > best_val or (v == best_val and (dx, dy) < best):
            best_val = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]