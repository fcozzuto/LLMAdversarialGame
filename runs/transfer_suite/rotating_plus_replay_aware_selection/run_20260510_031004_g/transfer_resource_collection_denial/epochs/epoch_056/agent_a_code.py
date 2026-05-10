def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    best = None
    for t in resources:
        sd = cheb((sx, sy), t)
        od = cheb((ox, oy), t)
        # Prefer we are closer; tie-break for larger (od-sd), then nearer to us.
        key = (od - sd, -sd)
        if best is None or key > best[0]:
            best = (key, t)
    target = best[1]

    tx, ty = target
    dirs = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                # Order: reduce distance most; then prefer diagonals; then deterministic by dx,dy.
                nd = cheb((nx, ny), (tx, ty))
                diag = 1 if dx != 0 and dy != 0 else 0
                dirs.append((nd, -diag, dx, dy))
    # If directly moving is blocked, allow staying still as last resort.
    if not dirs:
        return [0, 0]
    dirs.sort()
    return [int(dirs[0][2]), int(dirs[0][3])]