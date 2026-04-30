def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # relative targeting: prefer resources we can reach no later than opponent
        rel_best = None
        rel_score = None
        if resources:
            for rx, ry in resources:
                d_me = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                beat = 1 if d_me <= d_op else 0
                # Primary: reach-first; Secondary: absolute closeness; Tertiary: deny opponent (larger gap)
                gap = d_op - d_me
                key = (beat, -gap, -d_me)
                if rel_best is None or key > rel_best:
                    rel_best = key
                    rel_score = (beat, gap, d_me, cheb(nx, ny, ox, oy))
        # If no resources, just move toward center while keeping away from obstacles
        center_bias = -abs(nx - cx) - abs(ny - cy)
        if resources:
            beat, gap, d_me, d_to_op = rel_score
            # Encourage denying: if we beat by a little, still prioritize; also discourage moving into opponent proximity too early
            score = (1000 * beat) + (-2 * d_me) + (3 * gap) + (-0.5 * d_to_op) + 0.01 * center_bias
        else:
            # explore deterministically: head to closer corner-free region via center bias
            score = center_bias
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]