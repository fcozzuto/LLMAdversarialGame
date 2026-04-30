def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def near_obst_pen(x, y):
        if (x, y) in obst: return 10**6
        p = 0
        for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1),(x-1,y-1),(x+1,y+1),(x-1,y+1),(x+1,y-1)):
            if (nx, ny) in obst: p += 3
        return p

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    parity = observation.get("turn_index", 0) % 2

    if not resources:
        # deterministic fallback: go toward center-ish or away from corner if obstacle blocks
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                v = -10**7
            else:
                v = -cheb(nx, ny, tx, ty) - 0.1 * near_obst_pen(nx, ny)
            if bestv is None or v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        pen = near_obst_pen(nx, ny)
        if pen >= 10**5:
            continue

        # Evaluate best target resource for this next cell
        # Objective: maximize (dist(opponent, r) - dist(self_next, r)) with urgency, plus defensive term.
        best_target = None
        best_score_for_move = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            urgency = 1.0 / (1 + ds)
            if parity == 0:
                score = (do - ds) + 2.0 * urgency
            else:
                # defensive/denial: prefer moves that keep opponent's distance advantage smaller
                score = 0.7 * (do - ds) + 2.2 * urgency - 0.05 * cheb(nx, ny, ox, oy)
            if best_score_for_move is None or score > best_score_for_move:
                best_score_for_move = score
                best_target = (rx, ry)

        # tie-breaker: prefer closer to chosen target, then safer (lower obstacle penalty)
        rx, ry = best_target
        ds_now = cheb(nx, ny, rx, ry)
        total_val = best_score_for_move - 0.03 * pen - 0.001 * ds_now

        if best_val is None or total_val > best_val:
            best_val = total_val
            best_move = [dx, dy]

    return best_move