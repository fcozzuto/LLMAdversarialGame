def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles_raw = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    resources_raw = observation.get("resources", []) or []
    resources = []
    for r in resources_raw:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y) and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    best = None
    for x, y in resources:
        md = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        key = (md - od, md, x, y)
        if best is None or key < best[0]:
            best = (key, (x, y))
    tx, ty = best[1]

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    cand = []
    # Prefer direct direction, then axis alternatives, then stay.
    for a, b in [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0)]:
        nx, ny = sx + a, sy + b
        if inb(nx, ny) and (nx, ny) not in obs:
            cand.append((a, b))
        if len(cand) >= 1 and (a, b) == (dx, dy):
            break

    if not cand:
        return [0, 0]

    return [int(cand[0][0]), int(cand[0][1])]