def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    if w < 1 or h < 1 or len(sp) < 2 or len(op) < 2:
        return [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(x, y):
        return abs(x - ox) + abs(y - oy)

    def clearance(x, y):
        if not obstacles:
            return 99
        best = 10**9
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        return best if best != 10**9 else 99

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = md(nx, ny)
        clr = clearance(nx, ny)
        edge = min(nx, w - 1 - nx, ny, h - 1 - ny)
        # Key: primarily minimize distance to opponent; secondarily avoid obstacles; then prefer moves toward center.
        key = (d, -clr, -(edge), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        # If all moves invalid due to obstacles/bounds, stay.
        return [0, 0]
    return [int(best[0]), int(best[1])]