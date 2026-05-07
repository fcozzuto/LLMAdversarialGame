def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if resources:
        best_r = None
        best_gain = -10**9
        for rx, ry in resources:
            sd = dist((sx, sy), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            gain = (od - sd) * 10 - sd
            if best_r is None or gain > best_gain:
                best_r, best_gain = (rx, ry), gain
        tx, ty = best_r
        target_dirs = [(0, 0)] + [d for d in dirs if d != (0, 0) and ((sx + d[0] == tx) or (sy + d[1] == ty))]
        cand_dirs = target_dirs if target_dirs else dirs

        best_dir = None
        best_val = -10**18
        for dx, dy in cand_dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles:
                continue
            sd = dist((nx, ny), (tx, ty))
            od = dist((ox, oy), (tx, ty))
            val = (od - sd) * 10 - sd
            if best_dir is None or val > best_val:
                best_dir, best_val = (dx, dy), val
        if best_dir is not None:
            return [best_dir[0], best_dir[1]]

    # Fallback: chase opponent, avoid obstacles, deterministic tiebreak by dir order.
    best_dir = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        val = -dist((nx, ny), (ox, oy))
        if best_dir is None or val > best_val:
            best_dir, best_val = (dx, dy), val
    if best_dir is None:
        return [0, 0]
    return [best_dir[0], best_dir[1]]