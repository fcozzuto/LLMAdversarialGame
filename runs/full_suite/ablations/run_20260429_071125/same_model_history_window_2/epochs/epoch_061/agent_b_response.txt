def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = None
    best_move = [0, 0]

    # If no resources are reported, head toward center to improve future pickup chances.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best_score = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            score = -cheb(nx, ny, tx, ty)
            # tie-break deterministically by move order
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
        return best_move

    # Core strategy: move to positions where we are closer than the opponent to as many resources as possible.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        self_min = cheb(nx, ny, ox, oy)  # mild deterrent from getting too close (keeps safe routes)
        score = 0
        self_closest = 10**9
        opp_closest = 10**9
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if sd < self_closest: self_closest = sd
            if od < opp_closest: opp_closest = od
            diff = od - sd  # positive means we are nearer than opponent
            if diff > 0:
                score += diff * 10 + (1 if sd == 0 else 0)
            else:
                score += diff  # small penalty for being behind
        # Encourage taking the nearest advantage and slightly avoid direct proximity to opponent.
        score -= self_min
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            # deterministic tie-break: prefer moves with smaller (dx,dy) lexicographically after best_score match
            if (dx, dy) < (best_move[0], best_move[1]):
                best_move = [dx, dy]

    return best_move