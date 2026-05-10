def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(lst):
        s = set()
        if not lst:
            return s
        for c in lst:
            if c and len(c) >= 2:
                s.add((int(c[0]), int(c[1])))
        return s

    obstacles = to_set(observation.get("obstacles"))
    resources = to_set(observation.get("resources"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    self_t = to_set(observation.get("self_territory"))
    opp_t = to_set(observation.get("opponent_territory"))

    if resources:
        targets = list(resources)
    elif unclaimed:
        targets = list(unclaimed)
    else:
        targets = list(opp_t) if opp_t else [(sx, sy)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Intercept: target cells close to opponent, while not too far from us
    tx, ty = sx, sy
    best_int = None
    for x, y in targets[:32]:
        if (x, y) in obstacles:
            continue
        val = man(ox, oy, x, y) - man(sx, sy, x, y)
        if best_int is None or val < best_int:
            best_int = val
            tx, ty = x, y

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            score = -10**15
        else:
            adj_obst = 0
            for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                if (nx + ax, ny + ay) in obstacles:
                    adj_obst += 1
            if (nx, ny) in self_t:
                cell = 1
            elif (nx, ny) in opp_t:
                cell = 6
            elif (nx, ny) in unclaimed:
                cell = 10
            else:
                cell = 0
            score = (cell * 50) - man(nx, ny, tx, ty) - adj_obst * 8
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]