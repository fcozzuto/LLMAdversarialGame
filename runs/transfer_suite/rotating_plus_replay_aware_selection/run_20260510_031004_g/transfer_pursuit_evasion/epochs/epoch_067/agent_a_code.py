def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    def parse_xy(item):
        if isinstance(item, dict):
            for kx, ky in (("x", "y"), ("col", "row"), ("cx", "cy")):
                if kx in item and ky in item:
                    return int(item[kx]), int(item[ky])
            return None
        try:
            return int(item[0]), int(item[1])
        except Exception:
            return None

    resources = observation.get("resources", []) or []
    targets = []
    for r in resources:
        xy = parse_xy(r)
        if not xy:
            continue
        x, y = xy
        if 0 <= x < w and 0 <= y < h:
            targets.append((x, y))
    if not targets:
        dx = 0 if sx == ox else (1 if ox > sx else -1)
        dy = 0 if sy == oy else (1 if oy > sy else -1)
        cand = [(dx, 0), (0, dy), (dx, dy), (0, 0)]
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [int(dx), int(dy)]
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    tx, ty = min(targets, key=lambda t: (cheb(sx, sy, t[0], t[1]), abs(t[0] - ox) + abs(t[1] - oy)))
    dx = 0 if sx == tx else (1 if tx > sx else -1)
    dy = 0 if sy == ty else (1 if ty > sy else -1)

    options = [(dx, dy), (dx, 0), (0, dy)]
    if dx != 0 and dy != 0:
        options += [(dx, -dy), (-dx, dy), (-dx, -dy)]
    options += [(0, 0), (0, 1), (1, 0), (0, -1), (-1, 0)]

    for mx, my in options:
        mx, my = int(mx), int(my)
        if mx not in (-1, 0, 1) or my not in (-1, 0, 1):
            continue
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [mx, my]
    return [0, 0]