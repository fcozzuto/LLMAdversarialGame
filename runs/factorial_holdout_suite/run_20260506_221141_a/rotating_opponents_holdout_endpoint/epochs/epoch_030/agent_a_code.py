def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Choose resource I can reach first; break ties by closer and then by deterministic position.
    best = None
    for rx, ry in resources:
        myd = md(sx, sy, rx, ry)
        opd = md(ox, oy, rx, ry)
        lead = opd - myd
        key = (lead, -myd, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                # Prefer reducing distance to target, then advancing toward it along both axes, then deterministic.
                dist = md(nx, ny, tx, ty)
                curdist = md(sx, sy, tx, ty)
                improve = curdist - dist
                # Axis alignment score
                ax = -abs(tx - nx)
                ay = -abs(ty - ny)
                # Deterministic ordering: smaller dx then smaller dy
                moves.append((dist, -improve, -(ax + ay), dx, dy))
    if not moves:
        return [0, 0]
    moves.sort()
    _, _, _, dx, dy = moves[0]
    return [int(dx), int(dy)]