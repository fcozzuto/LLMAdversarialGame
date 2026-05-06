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
    if not resources:
        return [0, 0]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # If very close, step away deterministically to avoid losing tempo to a direct contest.
    dso = dist((sx, sy), (ox, oy))
    moves9 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if dso <= 2:
        best = None
        for dx, dy in moves9:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                score = (dist((nx, ny), (ox, oy)), -abs(nx - ox) - abs(ny - oy), -nx, -ny)
                if best is None or score > best[0]:
                    best = (score, dx, dy)
        return [int(best[1]), int(best[2])] if best else [0, 0]

    # Pick a resource where we have the biggest lead over the opponent (closer to us than them).
    best_cell = None
    best_key = None
    for rx, ry in resources:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # Prefer cells we can reach sooner; lightly penalize far resources to keep pressure.
        key = (od - sd, -sd, -rx, -ry)  # maximize lead, then smaller sd, then deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best_cell = (rx, ry)

    tx, ty = best_cell
    # Greedy obstacle-aware step toward target; if blocked, choose step that best preserves the lead advantage.
    candidates = []
    for dx, dy in moves9:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            lead = dist((ox, oy), (tx, ty)) - dist((nx, ny), (tx, ty))
            step_t = -dist((nx, ny), (tx, ty))
            toward_bias = -(abs(nx - tx) + abs(ny - ty))
            candidates.append((lead, step_t, toward_bias, -nx, -ny, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    return [int(candidates[0][5]), int(candidates[0][6])]