def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def to_set(key):
        pts = observation.get(key, []) or []
        s = set()
        for p in pts:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set("obstacles")
    selft = to_set("self_territory")
    opp = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")

    unclaimed_list = list(unclaimed)
    if len(unclaimed_list) > 40:
        unclaimed_list = unclaimed_list[:40]

    dirs = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    best_score = -10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def score_next(nx, ny):
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return -10**9
        s = 0
        if (nx, ny) in unclaimed:
            s += 6
        if (nx, ny) in selft:
            s += 2
        if (nx, ny) in opp:
            s -= 3
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ax, ay = nx + dx, ny + dy
                if (ax, ay) in unclaimed:
                    s += 2
                if (ax, ay) in opp:
                    s += 3
        if unclaimed_list:
            md = min(man(nx, ny, ux, uy) for ux, uy in unclaimed_list)
            s += 4 - md
        else:
            s += 4 - man(nx, ny, ox, oy)
        return s

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        sc = score_next(nx, ny)
        if sc > best_score:
            best_score = sc
            best = [dx, dy]
    return best if best is not None else [0, 0]