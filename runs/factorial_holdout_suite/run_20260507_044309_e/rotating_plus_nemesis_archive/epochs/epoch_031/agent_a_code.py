def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res.append((x, y))
        except:
            pass
    if not res:
        return [0, 0]

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    me = (sx, sy)
    him = (ox, oy)

    best = None
    best_key = None
    any_adv = False
    for t in res:
        d_me = cheb(me, t)
        d_op = cheb(him, t)
        adv = d_op - d_me
        if adv > 0:
            any_adv = True
        # Prefer: when we are closer, maximize advantage; otherwise, choose target where opponent is farthest.
        key = (0 if adv > 0 else 1, -adv, d_me, man(him, t))
        if best_key is None or key < best_key:
            best_key = key
            best = t

    tx, ty = best

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    move_dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    # obstacle-aware greedy: choose move minimizing distance to target, with small penalty for proximity to obstacles
    def obs_pen(nx, ny):
        p = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]:
            if (nx + dx, ny + dy) in blocked:
                p += 1
        return p

    best_m = None
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        d_to = cheb((nx, ny), (tx, ty))
        d_op = man((nx, ny), him)
        p_obs = obs_pen(nx, ny)
        # If we can’t get advantage target, prefer moves that increase distance from opponent slightly.
        key = (d_to, p_obs, -d_op if (best_key[0] == 1) else d_op, dx*0 + dy*0)
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]