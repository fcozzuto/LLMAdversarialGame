def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    rpos = []
    for r in resources:
        if isinstance(r, dict):
            p = r.get("position")
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
            else:
                continue
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
        else:
            continue
        if inb(x, y) and (x, y) not in blocked:
            rpos.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not rpos:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = None
        for (tx, ty) in rpos:
            sd = manh(sx, sy, tx, ty)
            od = manh(ox, oy, tx, ty)
            # Prioritize resources we can reach sooner; otherwise pick nearest.
            score = (sd - od, sd, tx, ty)
            if best is None or score < best[0]:
                best = (score, tx, ty)
        tx, ty = best[1], best[2]

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        sd2 = manh(nx, ny, tx, ty)
        od2 = manh(ox, oy, tx, ty)
        # If we can beat opponent, push; if not, reduce gap or at least approach.
        val = (sd2 - od2, sd2, abs(tx - nx) + abs(ty - ny), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move