def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obs.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = None
        for x, y in resources:
            dme = cheb(sx, sy, x, y)
            dome = cheb(ox, oy, x, y)
            # Maximize advantage; break ties by closer-to-self (more urgent).
            val = (dome - dme, -dme)
            if best is None or val > best[0]:
                best = (val, (x, y))
        tx, ty = best[1]

    def obstacle_local_pen(x, y):
        pen = 0.0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obs:
                pen += 0.9
        if (x, y) in obs: pen += 5.0
        return pen

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obs:
            continue

        dme_n = cheb(nx, ny, tx, ty)
        dome_n = cheb(ox, oy, tx, ty)
        # Prefer moves that reduce our distance, while making the opponent's distance advantage smaller.
        my_term = dme_n
        opp_adv = (dome_n - dme_n)  # lower is better for us if it means opponent is less advantaged
        # Actually maximize our advantage => minimize opp_adv; use negative as score to pick max.
        score = (-my_term, -opp_adv)
        # Add safety penalty
        score = (score[0] - obstacle_local_pen(nx, ny), score[1])

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]