def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    best = None
    if resources:
        resources.sort()
        bestd = 10**18
        tx, ty = sx, sy
        for x, y in resources:
            d = abs(x - sx) + abs(y - sy)
            if d < bestd:
                bestd = d
                tx, ty = x, y
    else:
        tx, ty = ox, oy

    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if (nx, ny) == (ox, oy):
            continue
        # Primary: move closer to target; Secondary: stay away from opponent if resources exist
        score = abs(tx - nx) + abs(ty - ny)
        if resources:
            score += max(0, 3 - (abs(ox - nx) + abs(oy - ny)))
        cand.append((score, dx, dy))

    if not cand:
        # All moves blocked or into opponent; allow staying if legal
        if ok(sx, sy) and (sx, sy) != (ox, oy):
            return [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    cand.sort()
    return [int(cand[0][1]), int(cand[0][2])]