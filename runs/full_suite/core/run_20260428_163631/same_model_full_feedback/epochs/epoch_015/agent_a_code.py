def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def safe(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        dists = [(cheb(sx, sy, ox, oy), 0)]
        target_dir = 0
    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_dx, best_dy = 0, 0
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        # Collecting is always best.
        if (nx, ny) in obstacles:
            continue

        # Distance to opponent for contention control.
        oppd = cheb(nx, ny, ox, oy)

        # Distance to closest resource.
        mind = 10**9
        target = None
        for rx, ry in resources:
            if (rx, ry) == (nx, ny):
                mind = 0
                target = (rx, ry)
                break
            d = cheb(nx, ny, rx, ry)
            if d < mind:
                mind, target = d, (rx, ry)

        if mind == 0:
            score = 10**6
        else:
            score = 0
            # Primary: go toward closest resource.
            score += -mind * 120
            # Secondary: avoid letting opponent get strictly closer.
            opp_closest = 10**9
            for rx, ry in resources:
                d = cheb(ox, oy, rx, ry)
                if d < opp_closest:
                    opp_closest = d
            # If we reduce our mind relative to opponent, reward it.
            my_after = mind
            opp_now = opp_closest
            if opp_now > 0:
                score += (opp_now - my_after) * 18
            else:
                score += 0

            # Tertiary: mild pressure to move toward center when not collecting.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            score += -int(cheb(nx, ny, cx, cy) * 3)

            # Avoid collisions: prefer slightly larger distance from opponent.
            score += oppd * 2

        if score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [best_dx, best_dy]