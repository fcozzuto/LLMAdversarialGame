def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    my_pos = (sx, sy)
    opp_pos = (ox, oy)

    if not resources:
        for dx, dy in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    rs = min(resources, key=lambda r: (dist(my_pos, r), r[0], r[1]))
    ro = min(resources, key=lambda r: (dist(opp_pos, r), r[0], r[1]))

    if dist(my_pos, rs) <= dist(my_pos, ro) - 1:
        target = rs
    else:
        target = ro

    options = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    best = None
    best_score = None
    for dx, dy in options:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = abs(nx - target[0]) + abs(ny - target[1])
        oppd = abs(ox - target[0]) + abs(oy - target[1])
        score = (-nd, -(dist(my_pos, target) - nd), oppd)
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]