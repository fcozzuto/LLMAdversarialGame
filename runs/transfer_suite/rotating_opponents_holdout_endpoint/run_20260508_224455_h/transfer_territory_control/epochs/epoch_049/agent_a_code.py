def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    try:
        w = int(w)
        h = int(h)
    except:
        w, h = 8, 8

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = sp[0] if len(sp) > 0 else 0, sp[1] if len(sp) > 1 else 0
    px, py = op[0] if len(op) > 0 else w - 1, op[1] if len(op) > 1 else h - 1
    sx, sy, px, py = int(sx), int(sy), int(px), int(py)

    obs = set()
    for c in observation.get("obstacles", []) or []:
        if c is not None and len(c) >= 2:
            x, y = c[0], c[1]
            if x is not None and y is not None:
                try:
                    obs.add((int(x), int(y)))
                except:
                    pass

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score(nx, ny):
        d = (nx - px) * (nx - px) + (ny - py) * (ny - py)
        risk = 0
        for dx, dy in dirs:
            ax, ay = nx + dx, ny + dy
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obs:
                risk += 1
        return (d, risk)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        sc = score(nx, ny)
        if best is None or sc < best_score:
            best_score = sc
            best = [dx, dy]

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return best