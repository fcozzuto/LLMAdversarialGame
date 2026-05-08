def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    cx, cy = (w - 1) // 2, (h - 1) // 2
    if not resources:
        tx, ty = cx, cy
    else:
        best = None
        tx, ty = resources[0]
        for (x, y) in resources:
            dx, dy = sx - x, sy - y
            d = dx * dx + dy * dy
            if best is None or d < best:
                best = d
                tx, ty = x, y

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_step = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = abs(nx - tx) if abs(nx - tx) > abs(ny - ty) else abs(ny - ty)
        score = dist * 10 + (1 if (nx, ny) == (int(op[0]), int(op[1])) else 0)
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_step):
            best_score = score
            best_step = (dx, dy)

    dx, dy = best_step
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    nx, ny = sx + dx, sy + dy
    if not inb(nx, ny):
        dx, dy = 0, 0
    return [int(dx), int(dy)]