def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            dopp = man(nx, ny, ox, oy)
            val = (dopp, -dx, -dy, nx + ny)
            if best is None or val > best:
                best = val
                bestmv = [dx, dy]
        return bestmv

    md_res = None
    for (rx, ry) in resources:
        selfd = man(sx, sy, rx, ry)
        oppd = man(ox, oy, rx, ry)
        # Prefer resources where we have an approach advantage vs opponent.
        # If we're behind, strongly discourage.
        advantage = (oppd - selfd)
        # Also gently prefer central-ish resources.
        center_bias = -abs(rx - (w - 1) / 2) - abs(ry - (h - 1) / 2)
        val = advantage * 10 + center_bias
        if md_res is None or val > md_res[0]:
            md_res = (val, rx, ry)

    _, tx, ty = md_res

    best = None
    bestmv = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_to_target = man(nx, ny, tx, ty)
        d_opp = man(nx, ny, ox, oy)
        # Aggressively close to target while avoiding being too close to opponent.
        # Deterministic tie-breaking via coordinates.
        val = (-d_to_target, d_opp, -(dx == 0 and dy == 0), nx, ny)
        if best is None or val > best:
            best = val
            bestmv = [dx, dy]

    return bestmv