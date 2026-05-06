def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in blocked

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = []
    for r in resources:
        if isinstance(r, dict):
            pos = r.get("position", None)
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                targets.append((pos[0], pos[1]))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((r[0], r[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_target = None
    best_tval = None

    if targets:
        for tx, ty in targets:
            if not legal(tx, ty):
                continue
            sd = man((sx, sy), (tx, ty))
            od = man((ox, oy), (tx, ty))
            # Prefer resources we can reach first; otherwise contest by making it harder to deny.
            tval = (1000 - 5 * sd) + (300 - 2 * od) if sd <= od else (500 - 4 * sd - 3 * od)
            if best_tval is None or tval > best_tval:
                best_tval = tval
                best_target = (tx, ty)

    if best_target is None:
        # No usable resource: maximize distance from opponent.
        best = (0, 0)
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = man((nx, ny), (ox, oy))
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    tx, ty = best_target
    sd0 = man((sx, sy), (tx, ty))
    contested = man((ox, oy), (tx, ty)) <= sd0

    best = (0, 0)
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        sd = man((nx, ny), (tx, ty))
        od = man((nx, ny), (ox, oy))
        # If contested, strongly prioritize pulling away from opponent while still approaching.
        v = (-3.0 * sd) + (0.9 * od) + (50 if (nx, ny) == (tx, ty) else 0)
        if contested:
            v += 1.5 * od
            v -= 2.0 * man((ox, oy), (tx, ty)) * (0.01)
        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]