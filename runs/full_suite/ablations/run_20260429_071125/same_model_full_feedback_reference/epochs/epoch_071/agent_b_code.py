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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    center = (w // 2, h // 2)
    target_list = resources if resources else [center]

    best_move = [0, 0]
    best_val = -10**18
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Evaluate by the best "contested advantage" we can maintain from the next cell.
        # Advantage: (opponent distance - our distance); higher is better.
        val = -10**18
        for rx, ry in target_list:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            s = opp_d - our_d
            # Tie-break: prefer moves that also reduce our distance to the closest target we can contest.
            t = -our_d
            if s > val or (s == val and t > val):
                val = s
        # Additional tie-break for determinism: lexicographic on move preference.
        if val > best_val or (val == best_val and [dx, dy] < best_move):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]