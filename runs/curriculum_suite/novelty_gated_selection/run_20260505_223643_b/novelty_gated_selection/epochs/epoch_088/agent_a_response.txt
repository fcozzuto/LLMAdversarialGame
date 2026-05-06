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
    dirs = moves  # deterministic ordering

    def cheb_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_move = [0, 0]
    best_score = None

    # Denial heuristic: pick move that maximizes (self_best - opp_best) to resources
    # using Chebyshev distance (diagonal-friendly).
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        self_best = None
        opp_best = None
        for rx, ry in resources:
            sd = cheb_dist(nx, ny, rx, ry)
            od = cheb_dist(ox, oy, rx, ry)
            # self_best: smallest distance to any resource
            if self_best is None or sd < self_best:
                self_best = sd
            # opp_best: smallest distance from opponent to any resource
            if opp_best is None or od < opp_best:
                opp_best = od

        if self_best is None:
            continue

        # Tie-breakers: prefer cells that are closer to some resource and that keep distance from opponent
        min_self_cell = None
        min_opp_r = None
        for rx, ry in resources:
            sd = cheb_dist(nx, ny, rx, ry)
            if min_self_cell is None or sd < min_self_cell:
                min_self_cell = sd
                # for min_opp_r tie-break, compute opp distance to that same resource
                min_opp_r = cheb_dist(ox, oy, rx, ry)

        lead = (opp_best - self_best)  # higher is better
        # Slightly punish stepping toward opponent to counter diagonal_probe "contact"
        contact = cheb_dist(nx, ny, ox, oy)
        score = (lead, -min_self_cell, -contact, nx, ny)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move