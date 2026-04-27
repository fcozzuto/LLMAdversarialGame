def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18
    best_tie = 10**18

    cx, cy = w // 2, h // 2

    for dx, dy in dirs:
        nx, ny = int(sx) + dx, int(sy) + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        if res:
            myd_to_best = 10**9
            oppd_to_best = -10**9
            # Choose the resource giving us the highest distance advantage, then pick move maximizing that advantage.
            for rx, ry in res:
                md = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                if od - md > oppd_to_best - myd_to_best:
                    myd_to_best = md
                    oppd_to_best = od
                # early skip if md is very small? keep deterministic; no randomness.
            advantage = oppd_to_best - myd_to_best
            # Slightly prefer closer to the chosen resource.
            score = advantage * 100 - myd_to_best
            tie = myd_to_best
        else:
            score = cheb(nx, ny, cx, cy) * -1 + cheb(nx, ny, ox, oy)  # go toward center, away from opponent
            tie = cheb(nx, ny, cx, cy)

        if score > best_score or (score == best_score and tie < best_tie):
            best_score = score
            best_tie = tie
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]