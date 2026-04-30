def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def steps(x1, y1, x2, y2):
        dx, dy = abs(x1 - x2), abs(y1 - y2)
        return dx if dx > dy else dy

    def best_target_score(r):
        rx, ry = r
        ds = steps(sx, sy, rx, ry)
        do = steps(ox, oy, rx, ry)
        return (ds - do, ds, -rx, -ry)  # minimize ds-do, then closer to us, then deterministic tie-break

    resources_sorted = sorted(resources, key=best_target_score)
    target = resources_sorted[0]
    tx, ty = target

    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        ns = steps(nx, ny, tx, ty)
        no = steps(ox, oy, tx, ty)

        # If we improve our time-to-target and keep ahead of opponent, that's best.
        # Add small bonus for moving away from opponent generally to reduce contention.
        score = (
            ns - no,                    # lower is better (we want ns < no)
            ns,                         # then shortest for us
            -abs(nx - ox) - abs(ny - oy),  # spread
            -abs((nx + ny) - (tx + ty)),    # small stability toward target corridor
            dx == 0 and dy == 0        # prefer moving if tie
        )
        if best is None or score < best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]