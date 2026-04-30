def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    me = (sx, sy)
    op = (ox, oy)

    best_move = legal[0]
    best_score = -10**18

    if resources:
        op_near = min(man(op, r) for r in resources)
        for dx, dy in legal:
            nme = (sx + dx, sy + dy)
            my_near = min(man(nme, r) for r in resources)
            score = (op_near - my_near)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
    else:
        op_dist = man(me, op)
        for dx, dy in legal:
            nme = (sx + dx, sy + dy)
            score = man(nme, op)
            if score > best_score or (score == best_score and score != op_dist):
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]