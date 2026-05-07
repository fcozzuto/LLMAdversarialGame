def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            sc = -md(nx, ny, ox, oy)
            if best is None or sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    # Intercept mode: if opponent is closer to some resource than we are, focus on the most dangerous one.
    intercept = None
    best_lead = -10**9
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        lead = od - sd  # positive means opponent is closer
        if lead > best_lead:
            best_lead = lead
            intercept = (rx, ry)

    if best_lead <= 0:
        target = max(resources, key=lambda c: (md(ox, oy, c[0], c[1]) - md(sx, sy, c[0], c[1]), -md(sx, sy, c[0], c[1])))
    else:
        target = intercept

    # Choose move that increases our chance on that target, with light tie-break for also not worsening beyond needed.
    tx, ty = target
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sd = md(nx, ny, tx, ty)
        od = md(ox, oy, tx, ty)
        win_est = (od - sd)  # larger -> we are closer than opponent (or opponent farther)
        # If already "ahead" on target, prefer shorter time to collect; otherwise prefer reducing opponent advantage.
        tiebias = -sd
        sc = (win_est * 100) + tiebias
        if best is None or sc > best[0] or (sc == best[0] and (dx, dy) < (best[1], best[2])):
            best = (sc, dx, dy)
    return [best[1], best[2]]