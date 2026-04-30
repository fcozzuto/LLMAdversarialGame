def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    pref = [(1, 1), (0, 1), (1, 0), (1, -1), (0, 0), (-1, 0), (0, -1), (-1, 1), (-1, -1)]
    if ok(sx, sy) is False:
        for dx, dy in pref:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    best_move = [0, 0]
    best_score = -10**18
    have_resources = len(resources) > 0
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        oppd = man(nx, ny, ox, oy)
        if have_resources:
            mind = 10**9
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                if d < mind:
                    mind = d
            score = (1000 - mind) * 10 + oppd
        else:
            score = oppd
        if (nx, ny) == (w - 1, h - 1) or (nx == w - 1 and ny == h - 1):
            score += 5
        if score > best_score or (score == best_score and (dx, dy) in pref):
            best_score = score
            best_move = [int(dx), int(dy)]
    return best_move