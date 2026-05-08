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

    myt = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                myt.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.append((x, y))
    if not unclaimed:
        unclaimed = list(myt)

    best = None
    bestd = 10**18
    for (tx, ty) in unclaimed:
        d = abs(tx - sx) + abs(ty - sy)
        if d < bestd:
            bestd = d
            best = (tx, ty)

    tx, ty = best if best is not None else (ox, oy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            dist_target = abs(tx - nx) + abs(ty - ny)
            dist_opp = abs(ox - nx) + abs(oy - ny)
            score = dist_target * 2 - dist_opp
            candidates.append((score, abs(dx) + abs(dy), dx, dy))
    candidates.sort()
    for _, _, dx, dy in candidates:
        if dx != 0 or dy != 0:
            return [int(dx), int(dy)]
    return [0, 0]