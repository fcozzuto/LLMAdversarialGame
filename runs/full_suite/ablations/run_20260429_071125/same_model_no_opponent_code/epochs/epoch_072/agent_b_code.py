def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manhattan(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0:
            ax = -ax
        if ay < 0:
            ay = -ay
        return ax + ay

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort()
    opp_move_pref = (1 if ox < sx else -1 if ox > sx else 0, 1 if oy < sy else -1 if oy > sy else 0)

    best = None
    best_val = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        if resources:
            score = 0
            # Prefer resources where we are more likely to beat opponent deterministically.
            # Use both distance advantage and proximity to avoid oscillations.
            for rx, ry in resources:
                myd = manhattan(nx, ny, rx, ry)
                opd = manhattan(ox, oy, rx, ry)
                adv = opd - myd  # positive if I'm closer
                # If I can reach sooner, strongly prefer; otherwise lightly consider.
                if adv > 0:
                    score += 2000 + 30 * adv - 3 * myd
                else:
                    score += 5 * adv - 2 * myd
            # Encourage shorter overall progress to any resource
            mind = min(manhattan(nx, ny, rx, ry) for rx, ry in resources)
            score += 40 * (16 - mind)  # grid-limited normalization
            # Safety: avoid stepping too close to opponent if no clear advantage
            if score < 1000:
                score -= 25 * cheb(nx, ny, ox, oy)
            # Minor bias: break ties by moving away from opponent if close
            score += -3 * cheb(nx, ny, ox, oy)
        else:
            # No resources visible: drift toward center while keeping distance from opponent
            cx, cy = (w - 1) // 2, (h - 1) // 2
            score = 100 - manhattan(nx, ny, cx, cy) - 10 * cheb(nx, ny, ox, oy)
            if dx == opp_move_pref[0] and dy == opp_move_pref[1]:
                score -= 8

        if score > best_val:
            best_val = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]