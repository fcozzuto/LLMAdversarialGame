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
    near_obs_dirs = dirs

    def obstacle_penalty(x, y):
        # avoid moving next to obstacles (simple local safety)
        pen = 0
        for dx, dy in near_obs_dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obs:
                pen += 0.7
        return pen

    def best_target_from(px, py):
        if not resources:  # head to center if no resources
            cx, cy = w // 2, h // 2
            return cx, cy
        best = None
        bestv = None
        for x, y in resources:
            md = cheb(px, py, x, y)
            od = cheb(ox, oy, x, y)
            # prefer resources where we are closer than opponent
            v = md - 1.05 * od
            # slight tie-break to reduce oscillation
            v += 0.01 * (x + y)
            if bestv is None or v < bestv:
                bestv = v
                best = (x, y)
        return best

    def score_move(nx, ny):
        tx, ty = best_target_from(nx, ny)
        md = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # higher is better: being closer than opponent and closer to target
        advantage = (od - md)
        # if opponent is very close to the chosen target, avoid committing too late
        urgency = 0
        if od <= 1 and md > od: urgency -= 2.5
        return advantage - 0.08 * md - obstacle_penalty(nx, ny) + urgency

    best_move = (0, 0)
    best_score = None
    # deterministic tie-break order: dirs as listed
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obs:
            continue
        sc = score_move(nx, ny)
        if best_score is None or sc > best_score or (sc == best_score and (dx, dy) < best_move):
            best_score = sc
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]