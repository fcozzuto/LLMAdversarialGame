def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def obst_pen(x, y):
        if not inb(x, y): return 10**6
        if (x, y) in obst: return 10**5
        p = 0
        if (x-1, y) in obst: p += 2
        if (x+1, y) in obst: p += 2
        if (x, y-1) in obst: p += 2
        if (x, y+1) in obst: p += 2
        return p

    # Target selection: maximize advantage (opponent farther than us), tie-break by ours closer and then fixed order.
    if not resources:
        target = ((w - 1) // 2, (h - 1) // 2)
    else:
        best = resources[0]
        best_adv = None
        for i in range(len(resources)):
            rx, ry = resources[i]
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if best_adv is None or adv > best_adv or (adv == best_adv and (sd < cheb(sx, sy, best[0], best[1]) or (sd == cheb(sx, sy, best[0], best[1]) and (rx, ry) < (best[0], best[1])))):
                best_adv = adv
                best = (rx, ry)
        target = best
    tx, ty = target

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): continue
        if (nx, ny) in obst: continue
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Lower is better: aim to minimize our distance, and maximize advantage against opponent.
        score = sd - 0.7 * od + obst_pen(nx, ny)
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]