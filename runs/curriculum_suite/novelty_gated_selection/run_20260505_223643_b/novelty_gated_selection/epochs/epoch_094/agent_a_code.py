def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs_order = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1), (0, 0)]
    moves = dirs_order

    def mindist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        return (dx * dx + dy * dy)

    best = None
    best_val = None

    if not resources:
        # Fall back to staying away from opponent while moving toward center-ish.
        center = (w // 2, h // 2)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                v = -mindist((nx, ny), center) + 0.35 * mindist((nx, ny), (ox, oy))
                if best_val is None or v > best_val or (v == best_val and (dx, dy) < best):
                    best_val = v
                    best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Greedy resource-seeking with explicit opponent-avoidance (counter center_rush).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        pos = (nx, ny)

        # Approach closest resource; add priority for resources that are reachable quickly.
        dres = min(mindist(pos, r) for r in resources)

        # Avoid getting too close to opponent; also discourage stepping into lines they could contest.
        dop = mindist(pos, (ox, oy))

        # Tie-break toward moving along axes first, then diagonals, then stay (deterministic by iteration order).
        v = -dres + 0.22 * dop

        if best_val is None or v > best_val:
            best_val = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]