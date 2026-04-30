def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy - (dx > dy and 0 or 0)  # unused trick; keep deterministic

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    have_res = len(resources) > 0
    target_mode = 1.0 if have_res else 0.0  # always deterministic switch
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Base: keep safe from obstacles only via validity; slight preference to advance
        adv = dist(sx, sy, ox, oy) - dist(nx, ny, ox, oy)
        score = 0.0

        if have_res:
            dmin = 10**9
            dsecond = 10**9
            closest = None
            for rx, ry in resources:
                d = dist(nx, ny, rx, ry)
                if d < dmin:
                    dsecond = dmin
                    dmin = d
                    closest = (rx, ry)
                elif d < dsecond:
                    dsecond = d
            # Prefer getting to a resource quickly, and steer toward the closest
            score += 3.5 * (-dmin)
            # If close enough, try to "lock onto" nearest rather than spread
            score += 1.5 * (-(dsecond if dsecond < 10**8 else dmin))
            # Slightly bias toward keeping progress toward that chosen resource
            if closest is not None:
                score += 0.8 * (dist(sx, sy, closest[0], closest[1]) - dist(nx, ny, closest[0], closest[1]))
            # Avoid letting opponent be closer to the same nearest resource
            if closest is not None:
                do = dist(ox, oy, closest[0], closest[1])
                score += 2.0 * (do - dmin)

        # When no resources remain, chase opponent directly
        score += (2.2 * target_mode) * adv
        if not have_res:
            score += 3.0 * (dist(ox, oy, nx, ny) - dist(ox, oy, sx, sy))

        # Deterministic tie-breaker: prefer smaller dx, then smaller dy
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]