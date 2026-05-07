def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    blocked = set()
    for p in (observation.get("obstacles", None) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if inside(px, py):
                blocked.add((px, py))

    resources = []
    for r in (observation.get("resources", None) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inside(rx, ry) and (rx, ry) not in blocked:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    best_val = None
    for cell in resources:
        sd = md((sx, sy), cell)
        od = md((ox, oy), cell)
        # Prefer resources where we have a tempo advantage; tie-break closer to us.
        val = (od - sd, -sd, -cell[0], -cell[1])
        if best_val is None or val > best_val:
            best_val = val
            best = cell

    tx, ty = best

    dx = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    dy = 0
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    nx, ny = sx + dx, sy + dy
    if (not inside(nx, ny)) or ((nx, ny) in blocked):
        # Try orthogonal/diagonal variants deterministically
        candidates = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0)]
        for cdx, cdy in candidates:
            nx, ny = sx + cdx, sy + cdy
            if inside(nx, ny) and (nx, ny) not in blocked:
                return [cdx, cdy]
        return [0, 0]

    return [dx, dy]