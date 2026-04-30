def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    rs = []
    for x, y in resources:
        x, y = int(x), int(y)
        if free(x, y):
            rs.append((x, y))
    if not rs:
        return [0, 0]

    # Pick target where we are relatively closer than opponent; tie-break by position and self distance
    best = None
    for x, y in rs:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        gain = od - sd  # larger is better
        # Prefer closer targets if gain ties; then deterministic position order
        key = (gain, -sd, -x, -y)
        if best is None or key > best[0]:
            best = (key, (x, y))
    tx, ty = best[1]

    # Greedy step toward target, with penalty for increasing distance and slight penalty for moving away from best-resources
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            sd2 = cheb(nx, ny, tx, ty)
            dist = cheb(sx, sy, tx, ty)
            improve = dist - sd2  # positive if getting closer
            # Secondary: keep toward other nearby resources deterministically
            near2 = 10**9
            for rx, ry in rs:
                d = cheb(nx, ny, rx, ry)
                if d < near2:
                    near2 = d
            # Score: primary improve, then lower sd2, then lower near2; deterministic tie by dx,dy
            score = (improve, -sd2, -near2, -dx, -dy)
            candidates.append((score, (dx, dy)))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0], reverse=True)
    return [int(candidates[0][1][0]), int(candidates[0][1][1])]