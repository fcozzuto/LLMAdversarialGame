def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best_r = None
    best_adv = -10**9
    for r in resources:
        dv = dist((sx, sy), r)
        do = dist((ox, oy), r)
        adv = (do - dv) * 10 - dv
        if adv > best_adv:
            best_adv = adv
            best_r = r

    tx, ty = (best_r if best_r is not None else (ox, oy))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_m = (0, 0)
    best_s = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d1 = dist((nx, ny), (tx, ty))
        d2 = dist((ox, oy), (tx, ty))
        adv = (d2 - d1) * 10 - d1
        if adv > best_s:
            best_s = adv
            best_m = (dx, dy)

    return [best_m[0], best_m[1]]