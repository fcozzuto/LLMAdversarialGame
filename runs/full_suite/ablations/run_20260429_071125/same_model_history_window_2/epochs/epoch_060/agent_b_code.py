def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = [0, 0]

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles:
                continue
            best_adv = None
            best_selfdist = None
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                adv = od - sd
                if best_adv is None or adv > best_adv or (adv == best_adv and sd < best_selfdist):
                    best_adv = adv
                    best_selfdist = sd
            # tie-break: prefer smaller opponent distance to reduce their counterplay, then deterministic order via move sum
            cand = (best_adv, -cheb(ox, oy, resources[0][0], resources[0][1]), -best_selfdist, dx + 2 * dy)
            if best is None or cand > best:
                best = cand
                best_move = [dx, dy]
    else:
        tx, ty = w // 2, h // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles:
                continue
            sd = cheb(nx, ny, tx, ty)
            cand = (-sd, dx + 2 * dy)
            if best is None or cand > best:
                best = cand
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]