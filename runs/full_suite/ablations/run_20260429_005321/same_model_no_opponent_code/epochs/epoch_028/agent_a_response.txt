def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break order above.

    best_move = (0, 0)
    best_score = None
    best_ds = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            nx, ny = sx, sy
        ds = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        # Evaluate by best resource swing vs opponent (opponent assumed stationary for one-step lookahead).
        score = -10**18
        for rx, ry in resources:
            dsr = cheb(nx, ny, rx, ry)
            dor = cheb(ox, oy, rx, ry)
            swing = (dor - dsr) * 100 - dsr
            # Small deterministic obstacle proximity penalty to reduce getting stuck near walls.
            prox = 0
            for ax, ay in ((nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1)):
                if (ax, ay) in obstacles:
                    prox += 1
            val = swing - prox
            if val > score:
                score = val
        if best_score is None or score > best_score or (score == best_score and ds < best_ds):
            best_score = score
            best_ds = ds
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]