def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            self_to_opp = cheb(nx, ny, ox, oy)
            best_adv = -10**18
            best_res_dist = 10**18
            best_res = None
            for tx, ty in resources:
                sd = cheb(nx, ny, tx, ty)
                od = cheb(ox, oy, tx, ty)
                adv = od - sd
                if adv > best_adv or (adv == best_adv and sd < best_res_dist):
                    best_adv = adv
                    best_res_dist = sd
                    best_res = (tx, ty)
            # Prefer winning the closest contested resource; avoid getting too close to opponent when equal.
            score = best_adv * 1000 - best_res_dist * 2 - self_to_opp * 1
            if best_res is not None:
                # Small tie-break: prefer moves that reduce distance to the chosen resource.
                score += -cheb(nx, ny, best_res[0], best_res[1]) * 0.1
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
    else:
        # No visible resources: drift toward center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            dist = abs(nx - cx) + abs(ny - cy)
            score = -dist
            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]