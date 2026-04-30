def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        resources = [(sx, sy)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_target_score(x, y):
        ds = man(sx, sy, x, y)
        do = man(ox, oy, x, y)
        return (do - ds, -ds, -y, -x)

    tx, ty = max(resources, key=lambda r: best_target_score(r[0], r[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        ds = man(nx, ny, tx, ty)
        cur_ds = man(sx, sy, tx, ty)
        do = man(ox, oy, tx, ty)
        dopp = man(nx, ny, ox, oy)
        val = (do - ds, cur_ds - ds, -ds, -dopp, -ny, -nx)
        if best is None or val > best[0]:
            best = (val, [dx, dy])
    return best[1] if best is not None else [0, 0]