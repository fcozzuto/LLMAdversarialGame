def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
        except:
            pass

    def cheb(a, b):
        return abs(a[0] - b[0]) if False else max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if not resources:
        return [0, 0]

    my = (sx, sy)
    opp = (ox, oy)
    best = None
    best_key = None
    for r in resources:
        myd = max(abs(r[0] - sx), abs(r[1] - sy))
        opd = max(abs(r[0] - ox), abs(r[1] - oy))
        adv = opd - myd
        key = (-adv, myd, r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best = r
    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            dist_to = max(abs(tx - nx), abs(ty - ny))
            dist_opp = max(abs(ox - nx), abs(oy - ny))
            toward = (dx != 0 or dy != 0)
            moves.append((dist_to, -dist_opp, -int(toward), dx, dy))
    if not moves:
        return [0, 0]
    moves.sort()
    return [int(moves[0][3]), int(moves[0][4])]