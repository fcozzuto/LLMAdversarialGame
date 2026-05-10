def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx, sy, ox, oy = 0, 0, 0, 0

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not inb(sx, sy):
        sx, sy = 0, 0

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    resources = observation.get("resources", []) or []
    rem = observation.get("remaining_resource_count", None)
    has_resources = True
    if rem is not None:
        try:
            has_resources = int(rem) > 0
        except:
            pass
    if not resources:
        has_resources = False

    nearest = None
    bestd = 10**9
    if resources and has_resources:
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = int(r[0]), int(r[1])
                if inb(rx, ry) or (0 <= rx < w and 0 <= ry < h):
                    d = abs(rx - sx) + abs(ry - sy)
                    if d < bestd:
                        bestd, nearest = d, (rx, ry)

    want = 1
    if not has_resources or nearest is None:
        want = -1  # flee opponent
    else:
        want = 1   # approach resource

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if want == 1:
            dres = man((nx, ny), nearest)
            score = -dres
            dop = man((nx, ny), (ox, oy))
            score += 0.01 * dop  # small bias to keep distance from opponent
        else:
            dop = man((nx, ny), (ox, oy))
            score = dop
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]