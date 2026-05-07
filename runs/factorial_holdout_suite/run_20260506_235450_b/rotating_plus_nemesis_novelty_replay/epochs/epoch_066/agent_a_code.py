def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (None, None))
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except:
            pass
    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = r
            resources.append((int(x), int(y)))
        except:
            pass

    if w <= 0 or h <= 0:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    bestv = -10**18
    have_opp = ox is not None and oy is not None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if resources:
            tv = -10**18
            for rx, ry in resources:
                d1 = man(nx, ny, rx, ry)
                v = -d1
                if have_opp:
                    d2 = man(ox, oy, rx, ry)
                    v += (d2 - d1)  # prefer resources closer than opponent
                tv = v if v > tv else tv
            v = tv
        else:
            # No resources known: drift toward center
            cx, cy = w // 2, h // 2
            v = -man(nx, ny, cx, cy)

        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]