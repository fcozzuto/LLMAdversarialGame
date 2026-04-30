def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best_delta = (0, 0)
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            best_res_adv = -10**18
            best_res_selfd = 10**18
            for tx, ty in resources:
                ds = cheb(nx, ny, tx, ty)
                do = cheb(ox, oy, tx, ty)
                adv = do - ds
                if adv > best_res_adv or (adv == best_res_adv and ds < best_res_selfd):
                    best_res_adv = adv
                    best_res_selfd = ds
            # Prefer higher advantage; break ties by being closer to that best resource; slight preference for moving.
            val = best_res_adv * 1000 - best_res_selfd + (abs(dx) + abs(dy)) * 0.01
            if val > best_val:
                best_val = val
                best_delta = (dx, dy)
        return [int(best_delta[0]), int(best_delta[1])]

    # No resources: move to reduce distance to opponent's likely frontier (towards center)
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_delta = (0, 0)
    best_d = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny, cx, cy)
        if d < best_d:
            best_d = d
            best_delta = (dx, dy)
    return [int(best_delta[0]), int(best_delta[1])]