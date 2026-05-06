def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = (-10**18, 10**9, 10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            nx, ny = sx, sy
        # avoid stepping into opponent vicinity (shadow archetype tends to contest)
        opp_adj = max(abs(nx - ox), abs(ny - oy))
        danger = 0
        if opp_adj <= 1:
            danger = 10
        elif opp_adj == 2:
            danger = 3

        best_for_move = -10**18
        best_tiebreak_dist = 10**9
        for rx, ry in resources:
            md = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            # advantage: positive when we can arrive first; bias toward shorter md
            val = (od - md) * 100 - md - (1 if (rx, ry) in obstacles else 0)
            if val > best_for_move or (val == best_for_move and md < best_tiebreak_dist):
                best_for_move = val
                best_tiebreak_dist = md

        # prefer moves that reduce distance to current best resource, and avoid danger
        key = (best_for_move - danger, best_tiebreak_dist, abs(nx - (w - 1)) + abs(ny - (h - 1)), dx, dy)
        if key > best:
            best = key

    return [int(best[3]), int(best[4])]