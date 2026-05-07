def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for a in obstacles:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obs.add((int(a[0]), int(a[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid_moves_from(x, y):
        out = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                out.append((dx, dy, nx, ny))
        return out

    if not resources:
        dm = []
        for dx, dy, nx, ny in valid_moves_from(sx, sy):
            dm.append((cheb(nx, ny, ox, oy), dx, dy))
        dm.sort(key=lambda t: (t[0], t[1], t[2]))
        return [dm[0][1], dm[0][2]] if dm else [0, 0]

    candidates = []
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = int(r[0]), int(r[1])
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer (larger advantage), then tie-break by smaller my distance.
        candidates.append((opd - myd, -myd, rx, ry))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[0], -t[1], t[2], t[3]))
    _, _, tx, ty = candidates[0]

    opts = []
    for dx, dy, nx, ny in valid_moves_from(sx, sy):
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # After moving, maximize our advantage over opponent for the target; then minimize our remaining distance.
        opts.append(((opd - myd), -myd, abs(nx - tx) + abs(ny - ty), dx, dy))
    opts.sort(key=lambda t: (-t[0], -t[1], t[2], t[3], t[4]))
    return [opts[0][3], opts[0][4]] if opts else [0, 0]