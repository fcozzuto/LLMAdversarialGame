def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

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

    def king_d(a, b):
        ax, ay = a
        bx, by = b
        da = abs(ax - bx)
        db = abs(ay - by)
        return da if da > db else db

    if not resources:
        tx, ty = ox, oy
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best_t = None
    best_val = None
    for t in resources:
        sd = king_d((sx, sy), t)
        od = king_d((ox, oy), t)
        # Race first (maximize opponent minus self distance), then prefer smaller own distance, then deterministic.
        val = (od - sd, -sd, -(t[0] + 31 * t[1]))
        if best_val is None or val > best_val:
            best_val = val
            best_t = t

    tx, ty = best_t
    step_x = 0 if tx == sx else (1 if tx > sx else -1)
    step_y = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    # Prefer diagonal/greedy, but if blocked by obstacle, fall back deterministically.
    candidates.append((step_x, step_y))
    candidates.append((step_x, 0))
    candidates.append((0, step_y))
    candidates.append((-step_x, 0))
    candidates.append((0, -step_y))
    candidates.append((0, 0))

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(dx), int(dy)]

    return [0, 0]