def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = int(observation.get("grid_width", 8))
    gh = int(observation.get("grid_height", 8))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < gw and 0 <= py < gh:
                obs.add((px, py))

    resources_in = observation.get("resources") or []
    resources = []
    for r in resources_in:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best = (0, 0)
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh): 
            continue
        if (nx, ny) in obs:
            continue

        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obs:
                    adj_pen += 1

        # pick target after move
        sc = -10**9
        for rx, ry in resources:
            dself = cheb(nx, ny, rx, ry)
            dopp = cheb(ox, oy, rx, ry)
            # prefer closer-to-resource and resources where we are advantaged
            v = (-dself) + 0.9 * (dopp - dself) - 0.15 * cheb(nx, ny, ox, oy) - 0.3 * adj_pen
            if v > sc:
                sc = v

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]