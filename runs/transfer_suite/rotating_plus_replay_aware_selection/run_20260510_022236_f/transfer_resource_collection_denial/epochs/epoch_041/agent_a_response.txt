def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)
    res = [(int(x), int(y)) for x, y in resources if 0 <= int(x) < w and 0 <= int(y) < h]
    if not res:
        return [0, 0]
    if (sx, sy) in obs:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_to_obstacle(x, y):
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (x + ax, y + ay) in obs and not (ax == 0 and ay == 0):
                    return True
        return False

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny, dx, dy = sx, sy, 0, 0
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny, dx, dy = sx, sy, 0, 0

        self_best = 10**9
        opp_best = 10**9
        tie_break = 0
        # Evaluate how quickly we can reach a resource compared to opponent; prefer securing one first.
        for rx, ry in res:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if sd < self_best: self_best = sd
            if od < opp_best: opp_best = od
            # local target score
            # higher score is better; we maximize (opp_dist - self_dist) then prefer closer self_dist
            pass

        # Pick best target under scoring using same move nx,ny (recomputed for determinism)
        target_score = -10**9
        closest_self = 10**9
        closest_opp = 10**9
        for rx, ry in res:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            delta = od - sd
            # prioritize positive delta (we arrive first), otherwise minimize sd and maximize od
            score = delta * 100 - sd * 3 + od
            if score > target_score or (score == target_score and (sd < closest_self or (sd == closest_self and od < closest_opp))):
                target_score = score
                closest_self = sd
                closest_opp = od

        # Safety: discourage stepping adjacent to obstacles unless we are already collecting/adjacent.
        safety = -12 if adj_to_obstacle(nx, ny) and (closest_self > 0) else 0
        # Resource proximity bonus to avoid dithering when timing is similar.
        prox = -closest_self
        final = target_score + safety + prox

        if best_score is None or final > best_score:
            best_score = final
            best = [dx, dy]
    return best