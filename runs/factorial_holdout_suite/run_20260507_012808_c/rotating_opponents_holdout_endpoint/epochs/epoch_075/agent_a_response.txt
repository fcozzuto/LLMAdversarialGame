def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    # Heuristic: maximize (opp_dist - self_dist); if not ahead, minimize self_dist.
    best = None
    for rx, ry in resources:
        sd = man(rx, ry, sx, sy)
        od = man(rx, ry, ox, oy)
        gain = od - sd
        # Small deterministic tie-break to avoid jitter: prefer higher y, then higher x.
        tieb = (ry, rx)
        key = (gain, -sd, tieb)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    _, (tx, ty) = best

    # Choose one-step move that heads to target while avoiding immediate obstacle.
    dirs = [(0, 0)]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            dirs.append((dx, dy))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_move = [0, 0]
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_to = cheb(nx, ny, tx, ty)
        # Tie-break: prefer diagonal first (more efficient), then smaller self distance, then stable order.
        diag = 1 if dx != 0 and dy != 0 else 0
        key = (-diag, d_to, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move