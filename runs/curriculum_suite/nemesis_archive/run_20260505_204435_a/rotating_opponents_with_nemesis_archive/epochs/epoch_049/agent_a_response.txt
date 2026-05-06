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

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in blocked
    def md(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    if not legal(sx, sy):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if legal(sx + dx, sy + dy):
                    return [dx, dy]
        return [0, 0]

    rpos = []
    for r in resources:
        if isinstance(r, dict):
            p = r.get("position")
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
                if legal(x, y):
                    rpos.append((x, y))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if legal(x, y):
                rpos.append((x, y))
    if not rpos:
        return [0, 0]

    # Choose resource we can secure: maximize (opp_dist - our_dist), then closeness.
    best = None
    for (rx, ry) in rpos:
        du = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        score = (do - du, -du, -rx, -ry)
        if best is None or score > best[0]:
            best = (score, (rx, ry))
    target = best[1]

    # If opponent is strictly closer to all resources, use interception: go towards a point on their path
    # to the closest resource they can reach.
    all_opponent_closer = True
    for (rx, ry) in rpos:
        if md(sx, sy, rx, ry) <= md(ox, oy, rx, ry):
            all_opponent_closer = False
            break
    if all_opponent_closer:
        # Choose the resource opponent is closest to, then step toward it.
        r2 = min(rpos, key=lambda p: (md(ox, oy, p[0], p[1]), p[0], p[1]))
        rx, ry = r2
        # Use a deterministic "intercept" point halfway (clamped) between us and that resource.
        tx = (sx + rx) // 2
        ty = (sy + ry) // 2
        # If that point is illegal, fall back to the resource itself.
        target = (tx, ty) if legal(tx, ty) else (rx, ry)

    # Greedy move toward target with deterministic tie-breaking.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    tx, ty = target
    best_step = (None, None)
    best_dist = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = md(nx, ny, tx, ty)
        key = (d, abs(dx), abs(dy), dx, dy)
        if best_dist is None or key < best_dist:
            best_dist = key
            best_step = [dx, dy]
    return best_step if best_step[0] is not None else [0, 0]