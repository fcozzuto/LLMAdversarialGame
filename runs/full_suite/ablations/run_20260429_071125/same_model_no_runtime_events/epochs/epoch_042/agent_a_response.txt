def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not valid(sx, sy):
        for dx, dy in [(-1, -1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if resources:
        # Choose a "contested" target: good for us, bad for opponent.
        best_target = None
        best_tv = -10**9
        for rx, ry in resources:
            ds = kdist(sx, sy, rx, ry)
            do = kdist(ox, oy, rx, ry)
            # Favor closer to us, farther from opponent; slight bias to avoid extreme corners.
            tv = (do - ds) * 10 - ds - (rx + ry) * 0.01
            if tv > best_tv:
                best_tv = tv
                best_target = (rx, ry)
        tx, ty = best_target
    else:
        # No resources: move toward center.
        tx, ty = w // 2, h // 2

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds2 = kdist(nx, ny, tx, ty)
        do2 = kdist(ox, oy, tx, ty)
        # Evaluate: get closer to target, and (slightly) reduce opponent's ability to race it.
        val = -ds2 * 10 + (do2 - ds2) * 2
        # Obstacle repulsion
        if obstacles:
            rep = 0
            for ax, ay in obstacles:
                d = kdist(nx, ny, ax, ay)
                if d == 0:
                    rep += 1000
                elif d == 1:
                    rep += 80
                elif d == 2:
                    rep += 20
            val -= rep
        # Prefer symmetry-breaking deterministically toward decreasing distance
        if resources:
            if (nx, ny) == (tx, ty):
                val += 5000
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]