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
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # If opponent is close, bias towards denying nearby resources; otherwise push best advantage.
    opp_near = min(cheb(sx, sy, rx, ry) for rx, ry in resources) <= 2

    bestm = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        v = 0
        # Evaluate all resources with a deterministic "advantage" score
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Main objective: maximize (opponent is farther than us)
            advantage = do - ds
            # If opponent is already very close to some resource, prioritize denying it strongly
            danger = 0
            if opp_near:
                if do <= 2:
                    danger = 4
                elif do <= 3:
                    danger = 2
            # Prefer moving closer even when behind (to potentially swing)
            swing = max(0, 3 - ds)
            # Small preference to reduce absolute distance to center-ish for stability
            cx, cy = (w - 1) // 2, (h - 1) // 2
            center = cheb(nx, ny, cx, cy)
            v += (advantage * 10) + (swing * 1.5) + (danger * 1.2) - (center * 0.05)

        # Mild reactive term: discourage stepping to increase opponent's advantage excessively
        v -= cheb(nx, ny, ox, oy) * 0.02

        if v > bestv:
            bestv = v
            bestm = [dx, dy]

    return [int(bestm[0]), int(bestm[1])]