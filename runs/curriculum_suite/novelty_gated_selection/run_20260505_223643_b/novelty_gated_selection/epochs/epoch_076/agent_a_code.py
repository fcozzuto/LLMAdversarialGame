def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb_dist(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0: dx = -dx
        dy = y2 - y1
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_move = [0, 0]
    best_score = None

    # Aim to be earlier than opponent to the best remaining resource (resource_denier).
    # One-step greedy evaluation.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_to = []
        opp_to = []
        for rx, ry in resources:
            self_to.append(cheb_dist(nx, ny, rx, ry))
            opp_to.append(cheb_dist(ox, oy, rx, ry))
        # Choose the resource that gives maximal advantage: (opp_dist - self_dist),
        # then break ties by prioritizing smaller self_dist and slightly safer movement.
        adv_best = None
        self_best = None
        for i in range(len(resources)):
            self_d = self_to[i]
            opp_d = opp_to[i]
            adv = opp_d - self_d
            if adv_best is None or adv > adv_best:
                adv_best = adv
                self_best = self_d
            elif adv == adv_best and (self_best is None or self_d < self_best):
                self_best = self_d

        # Safety: prefer moves that don't let opponent immediately close too fast.
        opp_closest = None
        for i in range(len(resources)):
            self_d = self_to[i]
            opp_d = opp_to[i]
            if opp_closest is None or opp_d < opp_closest:
                opp_closest = opp_d
        safety = -0.05 * opp_closest

        score = adv_best + (-0.01 * self_best) + safety
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move