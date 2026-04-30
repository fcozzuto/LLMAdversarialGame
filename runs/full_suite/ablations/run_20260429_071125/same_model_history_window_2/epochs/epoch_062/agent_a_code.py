def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        # Choose a target we are closer to than the opponent; otherwise least bad contest.
        best = None
        for rx, ry in sorted(resources):
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            gap = od - sd  # positive => we are closer
            # Prefer win-now targets; then reduce our distance; then stabilize by x/y ordering.
            key = (-1 if gap <= 0 else -0, -gap, sd, rx, ry)  # gap-positive first
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    # Move greedily toward target while avoiding obstacles; deterministic tie-break.
    bestm = (10**9, 10**9, 10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_o = cheb(nx, ny, ox, oy)
        # Primary: reduce distance to target; secondary: avoid getting too close to opponent.
        # Tertiary: keep deterministic by preferring smallest (dx,dy) among equals.
        key = (d_to_t, -d_to_o, abs(dx) + abs(dy), dx, dy)
        if key < bestm:
            bestm = key
    return [int(bestm[3]), int(bestm[4])]