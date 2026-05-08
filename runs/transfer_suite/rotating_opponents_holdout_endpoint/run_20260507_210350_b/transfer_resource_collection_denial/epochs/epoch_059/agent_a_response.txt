def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    # Pick a target we can capture first (or at least with the biggest lead).
    best_t = None
    best_key = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - sd  # positive means we arrive no later than opponent
        # Prefer capturing lead; then prefer closer; then lower coordinate for determinism.
        key = (-(adv), sd, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    # Evaluate all legal deltas with obstacle avoidance (engine keeps us in place if invalid).
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_mv = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        if (nx, ny) in obstacles:
            sc = -10**9
        else:
            nsd = cheb(nx, ny, tx, ty)
            nod = cheb(ox, oy, tx, ty)
            # Improve our capture advantage; also discourage drifting away.
            adv = nod - nsd
            sc = adv * 1000 - nsd
            # Small tie-break to keep motion consistent: prefer decreasing cheb distance when possible.
            curd = cheb(sx, sy, tx, ty)
            sc += 0.01 * (curd - nsd)
            if dx == 0 and dy == 0:
                sc -= 0.02
        if best_score is None or sc > best_score:
            best_score = sc
            best_mv = [dx, dy]

    return best_mv