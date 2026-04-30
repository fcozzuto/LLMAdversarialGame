def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    res_set = set()
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    if not resources:
        # Move to increase distance from opponent (avoid getting blocked) while staying safe
        best = (-10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            score = cheb(nx, ny, ox, oy)
            if score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Prefer stepping onto a resource; otherwise maximize (opponent arrival - self arrival) for some target.
    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        if (nx, ny) in res_set:
            cand = 10**6 + cheb(nx, ny, ox, oy) * 0.001
        else:
            best_target = -10**18
            for tx, ty in resources:
                ds = cheb(nx, ny, tx, ty)
                do = cheb(ox, oy, tx, ty)
                if do == ds:
                    s = 0
                adv = do - ds  # positive means we arrive earlier
                # Favor large advantage and proximity (smaller ds); mild preference for staying mobile
                s = adv * 1000 - ds + (0.2 if (abs(tx - nx) + abs(ty - ny)) <= 1 else 0)
                if s > best_target:
                    best_target = s
            # Mildly discourage stepping toward opponent unless it improves target advantage
            opp_now = cheb(sx, sy, ox, oy)
            opp_after = cheb(nx, ny, ox, oy)
            closer_pen = (opp_after - opp_now) * 0.5  # if closer, negative
            cand = best_target - closer_pen

        if cand > best_score:
            best_score = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]