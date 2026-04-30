def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if inb(rx, ry) and (rx, ry) not in obs:
                res.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best_dx = 0
    best_dy = 0
    best_score = -10**18

    if not res:
        for dx, dy in moves:
            nx, ny = int(sx) + dx, int(sy) + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            score = cheb(nx, ny, ox, oy)
            if score > best_score:
                best_score = score
                best_dx, best_dy = dx, dy
        return [best_dx, best_dy]

    for dx, dy in moves:
        nx, ny = int(sx) + dx, int(sy) + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        best_adv = -10**18
        best_dm = 10**18
        for rx, ry in res:
            dm = cheb(nx, ny, rx, ry)
            do = cheb(int(ox), int(oy), rx, ry)
            adv = do - dm
            if adv > best_adv or (adv == best_adv and dm < best_dm):
                best_adv = adv
                best_dm = dm
        score = best_adv * 1000 - best_dm
        if score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [best_dx, best_dy]