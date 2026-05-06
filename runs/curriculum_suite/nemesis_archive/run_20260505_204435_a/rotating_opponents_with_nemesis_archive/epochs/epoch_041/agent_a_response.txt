def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in blocked

    def parse_pos(r):
        if isinstance(r, dict):
            pos = r.get("position")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                return (pos[0], pos[1])
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            return (r[0], r[1])
        return None

    targets = []
    for r in resources:
        p = parse_pos(r)
        if p is not None and legal(p[0], p[1]):
            targets.append(p)
    if not targets:
        return [0, 0]

    def steps(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # king-move distance

    deltas = [(dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
    if not legal(sx, sy):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    best = None
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my = (nx, ny)
        cur = 0
        for tx, ty in targets:
            t = (tx, ty)
            my_s = steps(my, t)
            op_s = steps((ox, oy), t)
            rel = op_s - my_s  # positive means we are closer
            # prioritize being closer; also speed; discourage moving into late/worse targets
            s = rel * 100 - my_s * 2
            cur = s if s > cur else cur
        # tie-break toward nearest reasonable target
        near = min(steps((nx, ny), t) for t in targets)
        score = cur - near * 0.5
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]