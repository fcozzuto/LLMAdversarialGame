def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (None, None)
    try:
        sx, sy = int(sx), int(sy)
    except:
        sx, sy = 0, 0
    if w <= 0 or h <= 0:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if inb(x, y):
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1)]
    best = None
    best_sc = -10**18

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    opp_present = ox is not None and oy is not None
    if opp_present:
        try:
            ox, oy = int(ox), int(oy)
        except:
            opp_present = False

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        score = 0
        if resources:
            dmin = 10**9
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                if d < dmin:
                    dmin = d
            score += -dmin * 10
        else:
            score += 0

        if opp_present and inb(ox, oy):
            d0 = man(nx, ny, ox, oy)
            score += d0 * 3

        if best is None or score > best_sc:
            best_sc = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]