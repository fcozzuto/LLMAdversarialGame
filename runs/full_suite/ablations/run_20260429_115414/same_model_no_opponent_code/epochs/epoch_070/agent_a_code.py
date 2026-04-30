def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    sp = set()
    for p in observation.get("self_path", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            sp.add((int(p[0]), int(p[1])))
    # only recent-ish points to keep penalty small
    recent_pen = set()
    rp = observation.get("self_path", []) or []
    for i in range(max(0, len(rp) - 6), len(rp)):
        p = rp[i]
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            recent_pen.add((int(p[0]), int(p[1])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    candidates = []
    if resources:
        resources_sorted = sorted(resources, key=lambda r: cheb(sx, sy, r[0], r[1]))
        candidates = resources_sorted[:5]
    else:
        candidates = []

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        val = 0
        if (nx, ny) in resources:
            val += 10000
        if candidates:
            d_me = min(cheb(nx, ny, rx, ry) for rx, ry in candidates)
            d_op = min(cheb(ox, oy, rx, ry) for rx, ry in candidates)
            val += 200 - d_me
            if d_op <= d_me:
                val -= 30
        if (nx, ny) in recent_pen:
            val -= 6
        if (nx, ny) in sp:
            val -= 1
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]