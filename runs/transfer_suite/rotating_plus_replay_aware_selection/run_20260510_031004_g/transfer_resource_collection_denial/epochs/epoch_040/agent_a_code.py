def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obs = set()
    for p in obstacles_list:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    # Choose a resource we are advantaged at collecting (minimize our dist, maximize opponent dist).
    best_r = None
    best_sc = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer larger advantage; then closer; then deterministic coordinate tie-break.
        sc = (od - sd) * 1000 - sd
        if best_sc is None or sc > best_sc or (sc == best_sc and (rx, ry) < best_r):
            best_sc = sc
            best_r = (rx, ry)

    rx, ry = best_r
    dirs = [-1, 0, 1]
    candidates = []
    for dx in dirs:
        for dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                candidates.append((dx, dy))
    # If all adjacent are blocked, allow staying.
    if not candidates:
        return [0, 0]

    # Pick move that best reduces distance to chosen resource; deterministic tie-break by (dx,dy).
    best_m = None
    best_d = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        d = cheb(nx, ny, rx, ry)
        if best_d is None or d < best_d or (d == best_d and (dx, dy) < best_m):
            best_d = d
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]