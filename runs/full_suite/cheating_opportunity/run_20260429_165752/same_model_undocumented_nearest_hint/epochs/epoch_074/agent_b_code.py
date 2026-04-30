def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
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
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    # If no visible resources, drift toward center while keeping distance from opponent.
    if not resources:
        cx, cy = (W - 1) // 2, (H - 1) // 2
        bestm = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -cheb(nx, ny, cx, cy) + 0.5 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                bestm = (dx, dy)
        return [int(bestm[0]), int(bestm[1])]

    # Choose move that improves "resource advantage": prefer resources where we're not slower than opponent.
    bestm = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        my_future = (nx, ny)
        # Local obstacle pressure: discourage moving into crowded obstacle neighborhoods.
        obs_pressure = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    obs_pressure += 1

        # Evaluate best target from this candidate position.
        cand_best = -10**18
        for rx, ry in resources:
            myd = cheb(my_future[0], my_future[1], rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Advantage: positive if we're at least as close as opponent.
            adv = opd - myd
            # Extra tie-break: align toward resource and keep some distance from opponent to avoid swaps.
            v = 3.0 * adv - 0.8 * myd - 0.2 * cheb(my_future[0], my_future[1], ox, oy)
            # If candidate steps onto a resource, strongly prefer.
            if my_future[0] == rx and my_future[1] == ry:
                v += 1000
            if v > cand_best:
                cand_best = v

        total = cand_best - 0.5 * obs_pressure
        if total > bestv:
            bestv = total
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]