def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    turns = int(observation.get("turns_remaining", 0) or 0)
    parity = (sx + sy + turns) & 1

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def res_key(r):
        rx, ry = r
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd  # prefer being closer than opponent
        if ((rx + ry) & 1) != parity:
            adv -= 0.25
        return (adv, -sd, -rx, -ry)

    target = max(resources, key=res_key)
    tx, ty = target

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        hit = 1 if (nx, ny) in obstacles else 0
        ds = man(nx, ny, tx, ty)
        do = man(nx, ny, ox, oy)  # mild: stay away from chasing opponent too hard
        score = (-hit, -(ds), do, dx, dy)
        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]