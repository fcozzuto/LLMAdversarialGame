def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                resources.append((x, y))

    if not resources:
        cx, cy = (W - 1) // 2, (H - 1) // 2
        resources = [(cx, cy)] if inb(cx, cy) else [(min(max(sx, 0), W - 1), min(max(sy, 0), H - 1))]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    target = min(resources, key=lambda r: man(sx, sy, r[0], r[1]))

    best_step = (0, 0)
    best_dist = 10**9
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = man(nx, ny, target[0], target[1])
        # Slight deterministic pressure to avoid walking into opponent if tie
        if d < best_dist or (d == best_dist and man(nx, ny, ox, oy) > man(sx, sy, ox, oy)):
            best_dist = d
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]