def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
        best = (-10**18, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            s = -d
            if s > best[0]:
                best = (s, dx, dy)
        return [best[1], best[2]] if best[0] > -10**17 else [0, 0]

    cur_sep = cheb(sx, sy, ox, oy)

    # Choose a resource where we have the biggest "race advantage"
    best_r = resources[0]
    best_adv = -10**18
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        adv = d_op - d_me
        if adv > best_adv:
            best_adv = adv
            best_r = (rx, ry)

    rx, ry = best_r

    best = (-10**18, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_new = cheb(nx, ny, rx, ry)
        d_old = cheb(sx, sy, rx, ry)
        # Prefer decreasing distance to target and creating separation from opponent
        sep_new = cheb(nx, ny, ox, oy)
        s = (d_old - d_new) * 5 + (sep_new - cur_sep) * 0.7
        # If very behind on the target, still bias toward movement that reduces distance most
        if best_adv < 0:
            s += (-d_new) * 0.3
        # Small tie-break: nudge toward center to keep options open
        cx, cy = w // 2, h // 2
        s += (-cheb(nx, ny, cx, cy)) * 0.02
        if s > best[0]:
            best = (s, dx, dy)

    return [best[1], best[2]] if best[0] > -10**17 else [0, 0]