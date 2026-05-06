def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                if (x, y) not in obst:
                    res.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not any(inb(sx + dx, sy + dy) for dx, dy in moves):
        return [0, 0]

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if res:
            bestd = min(manh((nx, ny), r) for r in res)
            dopp = manh((nx, ny), (ox, oy))
            key = (bestd, -dopp, abs(dx) + abs(dy), dx, dy)
        else:
            tx, ty = (w - 1) // 2, (h - 1) // 2
            key = (manh((nx, ny), (tx, ty)), -manh((nx, ny), (ox, oy)), abs(dx) + abs(dy), dx, dy)
        candidates.append((key, [dx, dy]))

    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]