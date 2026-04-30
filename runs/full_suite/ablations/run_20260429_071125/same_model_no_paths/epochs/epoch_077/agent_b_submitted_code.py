def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    res = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                res.append((x, y))

    if res:
        tx, ty = min(res, key=lambda t: max(abs(t[0] - sx), abs(t[1] - sy)) * 1000 + (t[1] - t[0]))
    else:
        tx, ty = (ox, oy)
        if not inb(tx, ty):
            tx, ty = (w // 2, h // 2)
            if not inb(tx, ty):
                tx, ty = (sx, sy)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = max(abs(nx - tx), abs(ny - ty))
        score = d * 100 + (dx, dy) != (0, 0)
        if best is None or score < best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))
    if best is None:
        return [0, 0]
    dx, dy = best[1]
    return [dx, dy]