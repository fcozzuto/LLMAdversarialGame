def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    unclaimed = to_set("unclaimed_cells")
    opp_ter = to_set("opponent_territory")
    self_ter = to_set("self_territory")

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    if unclaimed:
        candidates = list(unclaimed)
    elif opp_ter:
        candidates = list(opp_ter)
    else:
        candidates = [(w // 2, h // 2)]
        if not candidates:
            candidates = [(ox, oy)]

    candidates.sort(key=lambda c: (dist((sx, sy), c), c[0], c[1]))
    tx, ty = candidates[0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (10**9, 10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        inside_self = 1 if (nx, ny) in self_ter else 0
        d = dist((nx, ny), (tx, ty))
        score = (d, inside_self)
        if score < (best[0], best[1]):
            best = (score[0], score[1], dx, dy)
        elif score == (best[0], best[1]):
            if (dx, dy) < (best[2], best[3]):
                best = (score[0], score[1], dx, dy)

    return [int(best[2]), int(best[3])]