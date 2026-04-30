def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if any(x == sx and y == sy for (x, y) in resources):
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                moves.append((0, 0))
            else:
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_t = None
    best_key = None
    for x, y in resources:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        # prioritize resources where we are relatively closer than opponent
        advantage = do - ds
        # small tie-break to favor not-too-far targets deterministically
        key = (-advantage, ds, x, y)  # minimize -> maximize advantage
        if best_key is None or key < best_key:
            best_key = key
            best_t = (x, y)

    tx, ty = best_t if best_t is not None else (w // 2, h // 2)

    # prefer moves that get us closer to target; then deterministic tie-break
    def obstacle_grad(nx, ny):
        # count nearby obstacles to discourage getting stuck
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    c += 1
        return c

    best_move = None
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, nx, ny)
        og = obstacle_grad(nx, ny)
        # primary: minimize distance-to-target; secondary: reduce chance of opponent intercept by staying farther from opponent
        key = (d, og, -opp_d, nx, ny, dx, dy)
        if best is None or key < best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]