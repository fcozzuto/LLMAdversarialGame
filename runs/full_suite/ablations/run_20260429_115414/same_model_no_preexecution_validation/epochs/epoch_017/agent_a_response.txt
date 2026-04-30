def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obstacles:
        if p is None or len(p) < 2:
            continue
        px, py = int(p[0]), int(p[1])
        if 0 <= px < w and 0 <= py < h:
            obs_set.add((px, py))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in obs_set
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def obs_pen(x, y):
        if not obs_set: return 0.0
        m = 10**9
        for px, py in obs_set:
            d = cheb(x, y, px, py)
            if d < m: m = d
        if m >= 2: return 0.0
        return 3.5 - 1.5 * m

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = w // 2, h // 2

    if resources:
        targets = []
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # prefer resources where we are closer (make ours win the race)
            val = d_me - 0.9 * d_op
            targets.append((val, d_me, rx, ry))
        targets.sort()
        # consider up to 4 best targets for speed/robustness
        targets = targets[:4]
    else:
        targets = []

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        if targets:
            local_best = None
            for _, _, rx, ry in targets:
                my_d = cheb(nx, ny, rx, ry)
                op_d = cheb(ox, oy, rx, ry)
                # encourage reaching faster and denying opponent, with obstacle awareness
                score = my_d - 1.05 * op_d + 0.08 * cheb(nx, ny, sx, sy) + obs_pen(nx, ny)
                if local_best is None or score < local_best:
                    local_best = score
            score = local_best
            # slight preference to increase distance from opponent
            score += 0.02 * cheb(nx, ny, ox, oy)
        else:
            score = cheb(nx, ny, cx, cy) - 0.35 * cheb(nx, ny, ox, oy) + obs_pen(nx, ny)

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    if legal(sx, sy):
        return [int(best_move[0]), int(best_move[1])]
    return [0, 0]