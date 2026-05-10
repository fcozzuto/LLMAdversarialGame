def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    resources = observation.get("resources", None)
    if resources is None:
        resources = observation.get("remaining_resource_count", None)
    if isinstance(resources, list):
        res_list = []
        for p in resources:
            try:
                x, y = int(p[0]), int(p[1])
                if inb(x, y) and (x, y) not in obstacles:
                    res_list.append((x, y))
            except Exception:
                pass
    else:
        res_list = []

    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        risk = man(nx, ny, ox, oy)
        if risk <= 1:
            away = -1000 + risk
        else:
            away = risk
        if res_list:
            target = min(res_list, key=lambda r: man(nx, ny, r[0], r[1]))
            gain = -man(nx, ny, target[0], target[1])
        else:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            gain = -man(nx, ny, cx, cy)
        scored.append((away * 10 + gain, dx, dy))

    if not scored:
        return [0, 0]
    scored.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(scored[0][1]), int(scored[0][2])]