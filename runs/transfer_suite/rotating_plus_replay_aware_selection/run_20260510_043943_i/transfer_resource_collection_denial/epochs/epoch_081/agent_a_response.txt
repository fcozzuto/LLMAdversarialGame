def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    # Pick the resource where we are currently most ahead (or least behind), with tie-breaks.
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0
    best_r = None
    best_key = None
    for rx, ry in resources:
        if not ok(rx, ry):
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        center = -abs(rx - cx) - abs(ry - cy) * 0.25
        key = (od - sd, -sd, center, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)
    if best_r is None:
        return [0, 0]
    rx, ry = best_r

    # Candidate moves ordered deterministically to favor diagonals that reduce distance.
    deltas = [(-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (-1, 0), (1, 0), (0, 1), (0, 0)]
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nsd = man(nx, ny, rx, ry)
        nod = man(ox, oy, rx, ry)
        # Main objective: maximize our advantage to the chosen target.
        # Secondary: move closer to target; tertiary: slight center bias to avoid dead-ends.
        adv = nod - nsd
        close = -nsd
        center = -abs(nx - cx) - abs(ny - cy)
        # Small tie-break to reduce oscillations: prefer moves that decrease both coordinates' distance.
        dxr = abs(nx - rx) - abs(sx - rx)
        dyr = abs(ny - ry) - abs(sy - ry)
        smooth = -(dxr * dxr + dyr * dyr)
        score = (adv, close, center, smooth)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move