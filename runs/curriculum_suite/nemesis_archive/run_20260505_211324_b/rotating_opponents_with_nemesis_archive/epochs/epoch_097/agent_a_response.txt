def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx if inb(nx, ny) else 0, dy if inb(nx, ny) else 0] if inb(nx, ny) else [0, 0]

    bestR = None
    bestAdv = -10**9
    bestSelfD = 10**9
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        adv = od - sd  # positive: we're closer
        if adv > bestAdv or (adv == bestAdv and sd < bestSelfD):
            bestAdv = adv
            bestSelfD = sd
            bestR = (rx, ry)

    rx, ry = bestR
    curSd = dist(sx, sy, rx, ry)

    bestMove = (0, 0)
    bestKey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nsd = dist(nx, ny, rx, ry)
        nod = dist(ox, oy, rx, ry)
        advAfter = nod - nsd
        # Prefer decreasing distance; then stronger advantage; then progress over stalling.
        key = (nsd <= curSd, -nsd, -advAfter, -abs(dx) - abs(dy))
        if bestKey is None or key > bestKey:
            bestKey = key
            bestMove = (dx, dy)

    dx, dy = bestMove
    return [int(dx), int(dy)]