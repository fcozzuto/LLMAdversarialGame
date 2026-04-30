def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def obstacle_near(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    pen += 1
        return pen

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        near_pen = obstacle_near(nx, ny)

        if resources:
            dres = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            ties = sum(1 for rx, ry in resources if cheb(nx, ny, rx, ry) == dres)
        else:
            dres, ties = 0, 0

        dop = cheb(nx, ny, ox, oy)

        # Deterministic scoring: prioritize getting closer to nearest resource,
        # avoid obstacle-adjacency, and slightly prefer staying away from opponent early.
        score = (
            dres * 10
            - dop * 1
            + near_pen * 3
            + ties * 0.01
            + cheb(nx, ny, 0, 0) * 0.0001
        )

        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])] if best is not None else [0, 0]