def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if unclaimed:
        candidates = unclaimed[:25]
    elif opp_terr:
        candidates = opp_terr[:25]
    elif self_terr:
        candidates = self_terr[:25]
    else:
        candidates = [(ox, oy)]

    best = None
    for tx, ty in candidates:
        if not inb(tx, ty) or (tx, ty) in obstacles:
            continue
        ds = man(sx, sy, tx, ty)
        do = man(ox, oy, tx, ty)
        score = ds - do  # prefer smaller (reach sooner than opponent)
        if best is None or (score, tx, ty) < best:
            best = (score, tx, ty)

    if best is None:
        return [0, 0]

    _, tx, ty = best
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    best_step = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds = man(nx, ny, tx, ty)
        do = man(nx, ny, ox, oy)
        # Prefer moving closer to target, while increasing distance from opponent
        step_score = (ds, do * -1, nx, ny)
        if best_step is None or step_score < best_step:
            best_step = step_score
            best_move = [dx, dy]

    return best_move if best_step is not None else [0, 0]