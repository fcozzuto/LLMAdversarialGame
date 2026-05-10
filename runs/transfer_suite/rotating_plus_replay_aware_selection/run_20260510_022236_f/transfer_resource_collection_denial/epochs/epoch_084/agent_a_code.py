def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    tr = int(observation.get("turns_remaining", 0))

    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid = []
    for x, y in resources:
        x, y = int(x), int(y)
        if inb(x, y) and (x, y) not in obs:
            valid.append((x, y))
    if not valid:
        return [0, 0]

    best = None
    for rx, ry in valid:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Strongly prefer resources we can reach earlier; otherwise pick one that minimizes opponent edge.
        score = (do - ds) * 100 - ds
        # Mild urgency: when late, don't go too far.
        if tr > 0:
            score -= max(0, ds - tr) * 30
        # Deterministic tiebreak: lower target x then y.
        score -= rx * 0.01 + ry * 0.0001
        if best is None or score > best[0]:
            best = (score, rx, ry)

    _, tx, ty = best
    stepx = 0
    if tx > sx: stepx = 1
    elif tx < sx: stepx = -1
    stepy = 0
    if ty > sy: stepy = 1
    elif ty < sy: stepy = -1

    candidates = []
    # Prefer diagonal toward target, then axial, then stay.
    candidates.append((stepx, stepy))
    candidates.append((stepx, 0))
    candidates.append((0, stepy))
    candidates.append((0, 0))

    best_m = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Choose move that maximizes our progress and minimizes opponent closeness to the same target.
        m = (cheb(ox, oy, tx, ty) - cheb(nx, ny, tx, ty)) * 10 + (cheb(ox, oy, nx, ny) * 0)
        # Deterministic tiebreak: prefer lexicographically smaller (dx,dy) among equal m.
        if best_m is None or m > best_m[0] or (m == best_m[0] and (dx, dy) < best_m[1]):
            best_m = (m, (dx, dy))

    if best_m is None:
        return [0, 0]
    dx, dy = best_m[1]
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]