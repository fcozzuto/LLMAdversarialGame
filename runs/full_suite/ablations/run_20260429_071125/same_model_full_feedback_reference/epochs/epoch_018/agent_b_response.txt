def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles or not resources:
        return [0, 0]

    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd  # higher is better (we are closer)
        # encourage also near-to-center-ish (avoid hugging far corners) via mild tie-break
        center_bias = - (abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0))
        key = (adv, -sd, center_bias, -max(0, adv), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    if sx == rx and sy == ry:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    preferred = (0 if rx == sx else (1 if rx > sx else -1), 0 if ry == sy else (1 if ry > sy else -1))

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    # try preferred step first (toward target)
    dx0, dy0 = preferred
    nx0, ny0 = sx + dx0, sy + dy0
    if valid(nx0, ny0):
        return [dx0, dy0]

    # otherwise, choose best alternative deterministically
    best_d = None
    best_m = None
    for dx, dy in dirs:
        if dx == 0 and dy == 0 and (sx + dx, sy + dy) == (sx, sy):
            continue
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = man(nx, ny, rx, ry)
        key = (-(dist), -abs((rx - nx)) - abs((ry - ny)), dx, dy)
        if best_m is None or key > best_m:
            best_m = key
            best_d = (dx, dy)

    if best_d is not None:
        return [int(best_d[0]), int(best_d[1])]
    return [0, 0]