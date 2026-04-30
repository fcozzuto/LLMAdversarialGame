def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    center = (w // 2, h // 2)
    targets = resources if resources else [center]

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Score: prefer getting closer to high-priority resources and being closer than opponent.
        score = 0
        for i, (tx, ty) in enumerate(targets):
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)

            # Capture pressure: higher when we can arrive sooner than opponent.
            diff = do - ds
            arrive = 1.0 / (1 + ds)
            lead = diff
            # Slight preference to earlier resources in deterministic ordering.
            bias = -0.001 * i

            score += 10.0 * lead + 5.0 * arrive + bias

        # Small strategic tie-break: move towards center if resources absent.
        if not resources:
            score += -0.1 * cheb(nx, ny, center[0], center[1])

        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move