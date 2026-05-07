def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    def cell_blocked(x, y):
        return (x, y) in obstacles

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def adj_obst_pen(x, y):
        if cell_blocked(x, y):
            return 10**6
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    pen += 1
        return pen

    best = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry) or cell_blocked(rx, ry):
            continue
        self_d = man(sx, sy, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        margin = opp_d - self_d  # positive means we are faster
        # If opponent is very close, avoid resources they are likely to snatch
        deny_risk = 0
        if opp_d <= 2 and self_d > opp_d:
            deny_risk = 5000 + 20 * (self_d - opp_d)
        # Prefer resources that also move away from opponent (helps vs denier)
        away = man(ox, oy, rx, ry)
        dist_pen = 2 * (self_d)  # keep progress
        pen = adj_obst_pen(rx, ry) + deny_risk + dist_pen
        # Add away term but keep it secondary to "we can reach first"
        score = 1000 * margin + 0.2 * away - pen
        cand = (score, -away, rx, ry)
        if best is None or cand > best:
            best = cand

    _, _, tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If the diagonal step is blocked by obstacle, fall back deterministically to one axis
    nx, ny = sx + dx, sy + dy
    if inb(nx, ny) and not cell_blocked(nx, ny):
        return [dx, dy]
    if dx != 0:
        nx2, ny2 = sx + dx, sy
        if inb(nx2, ny2) and not cell_blocked(nx2, ny2):
            return [dx, 0]
    if dy != 0:
        nx2, ny2 = sx, sy + dy
        if inb(nx2, ny2) and not cell_blocked(nx2, ny2):
            return [0, dy]
    return [0, 0]