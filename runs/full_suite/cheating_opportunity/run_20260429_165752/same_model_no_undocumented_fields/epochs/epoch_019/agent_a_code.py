def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    target_list = resources if resources else [(ox, oy)]

    best_move = (0, 0)
    best_d = 10**9
    best_t = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Deterministic tie-break: closest target, then lowest target coord.
        for tx, ty in target_list:
            d = manh(nx, ny, tx, ty)
            if d < best_d or (d == best_d and (ty < best_t or (ty == best_t and (tx < 0x7fffffff)))):
                best_d = d
                best_move = (dx, dy)
                best_t = ty
        if resources and resources:
            # If no resource list, target_list has only opponent position.
            pass

    return [best_move[0], best_move[1]]