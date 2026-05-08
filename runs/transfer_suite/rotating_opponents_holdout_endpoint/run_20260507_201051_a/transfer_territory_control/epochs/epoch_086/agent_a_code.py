def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not ok(sx, sy):
        for nx, ny in ((sx, sy), (0, 0), (1, 0), (0, 1), (1, 1), (2, 2)):
            nx, ny = int(nx), int(ny)
            if ok(nx, ny):
                sx, sy = nx, ny
                break
        else:
            return [0, 0]

    rx = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                rx.append((x, y))
    if not rx:
        rx = [(w // 2, h // 2)]

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    bx = by = 0

    def score(nx, ny):
        # Prefer getting closer to nearest resource, and away from opponent.
        dres = min(abs(nx - x) + abs(ny - y) for x, y in rx)
        dopp = abs(nx - ox) + abs(ny - oy)
        # Smaller dres is better; larger dopp is better.
        return (-dres, -dopp, nx, ny)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sc = score(nx, ny)
        if best is None or sc > best:
            best = sc
            bx, by = dx, dy

    return [int(bx), int(by)]