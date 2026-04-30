def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                resources.append((x, y))

    def sign(a):
        return (a > 0) - (a < 0)

    if resources:
        tx, ty = min(resources, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
        dx, dy = sign(tx - sx), sign(ty - sy)
        preferred = [(dx, dy)]
    else:
        dx, dy = sign(ox - sx), sign(oy - sy)
        preferred = [(dx, dy), (dx, 0), (0, dy)]

    tried = set()
    for cand in preferred + moves:
        cdx, cdy = int(cand[0]), int(cand[1])
        if (cdx, cdy) in tried:
            continue
        tried.add((cdx, cdy))
        nx, ny = sx + cdx, sy + cdy
        if valid(nx, ny):
            return [cdx, cdy]

    return [0, 0]