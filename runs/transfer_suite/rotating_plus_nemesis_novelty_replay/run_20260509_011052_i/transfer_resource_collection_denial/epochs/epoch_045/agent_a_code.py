def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    # Pick a target we can contest (or beat) with obstacle-aware greedy step.
    best_t = resources[0]
    best_val = -10**18
    for x, y in resources:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        # Strong preference to targets we can reach earlier; slight preference for closer.
        val = (do - ds) * 200 - ds
        # If opponent is very close, avoid giving them an easy uncontested pickup.
        if do <= 2 and ds > do:
            val -= (2 - (do - ds)) * 250 + manh(ox, oy, x, y)
        # If opponent is adjacent, also prefer targets that are farther from them.
        if do <= 1:
            val -= 120 * manh(ox, oy, x, y)
        if val > best_val:
            best_val = val
            best_t = (x, y)

    tx, ty = best_t

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break: smaller dx then dy.
    deltas = sorted(deltas, key=lambda d: (d[0], d[1]))

    best_move = (0, 0)
    best_dist = 10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in blocked:
            continue
        d = cheb(nx, ny, tx, ty)
        # Prefer shortest distance; if tie, prefer keeping x/y movement small then 0,0.
        if d < best_dist:
            best_dist = d
            best_move = (dx, dy)
        elif d == best_dist:
            if abs(dx) + abs(dy) < abs(best_move[0]) + abs(best_move[1]):
                best_move = (dx, dy)
            elif abs(dx) + abs(dy) == abs(best_move[0]) + abs(best_move[1]):
                if (dx, dy) < best_move:
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]