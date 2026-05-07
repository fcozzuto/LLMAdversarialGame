def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if not (isinstance(rx, int) and isinstance(ry, int)):
            continue
        if not inb(rx, ry):
            continue
        dme = cheb(sx, sy, rx, ry)
        dop = cheb(ox, oy, rx, ry)
        # Primary: win (opponent farther). Secondary: shorter for us.
        key = (dop - dme, -dme, -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]

    rx, ry = best
    step_options = []
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)
    for ax in (-1, 0, 1):
        for ay in (-1, 0, 1):
            if ax == 0 and ay == 0:
                ok = True
            else:
                ok = (ax == 0 or ax == dx or ax == -dx)
                # Allow diagonals/strafe: still bounded by one-step move
            nx, ny = sx + ax, sy + ay
            if inb(nx, ny):
                step_options.append((ax, ay, cheb(nx, ny, rx, ry)))

    if not step_options:
        return [0, 0]

    # Choose move that minimizes our distance to target; tie-break deterministically.
    step_options.sort(key=lambda t: (t[2], -(t[0] * 10 + t[1]), t[0], t[1]))
    return [int(step_options[0][0]), int(step_options[0][1])]