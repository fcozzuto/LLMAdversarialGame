def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    best = (float("-inf"), 0, 0)
    scored_any = False
    for dx, dy, nx, ny in legal:
        if resources:
            best_r = float("-inf")
            for rx, ry in resources:
                our_d = cheb(nx, ny, rx, ry)
                opp_d = cheb(ox, oy, rx, ry)
                if our_d == 0:
                    # Prefer immediate pickup strongly
                    val = 10_000 - opp_d
                else:
                    # Prefer resources where we are not slower than opponent
                    diff = opp_d - our_d  # positive means we're closer
                    val = diff * 50 - our_d
                    if our_d > opp_d:
                        val -= (our_d - opp_d) * 100  # heavily penalize being slower
                if val > best_r:
                    best_r = val
            # Small tie-breakers to reduce dithering
            opp_dist = cheb(nx, ny, ox, oy)
            val = best_r + opp_dist * 1
            scored_any = True
        else:
            # No resources: head toward center while not approaching opponent too much
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center_d = cheb(nx, ny, int(cx), int(cy))
            opp_dist = cheb(nx, ny, ox, oy)
            val = -center_d + opp_dist * 0.5
            scored_any = True

        if val > best[0]:
            best = (val, dx, dy)

    if not scored_any:
        return [0, 0]
    return [int(best[1]), int(best[2])]