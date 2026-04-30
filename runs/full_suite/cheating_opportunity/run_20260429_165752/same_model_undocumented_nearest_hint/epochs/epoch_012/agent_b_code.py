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
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def score_move(nx, ny):
        if not ok(nx, ny):
            return -10**9
        # Base: go to resource we can plausibly beat.
        if resources:
            best = -10**9
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Prefer resources closer to us than opponent by margin.
                # Also slightly favor moves that reduce our advantage short-term.
                rel = do - ds
                # If opponent is closer, we still might contest by minimizing ds.
                val = rel * 3.0 - ds * 1.0
                # Small tie-break: avoid getting too close to opponent (reduces contested collection risk).
                val -= cheb(nx, ny, ox, oy) * 0.15
                if val > best:
                    best = val
            return best
        # No visible resources: position to contest later and keep pressure.
        cx, cy = (W - 1) // 2, (H - 1) // 2
        d_center = cheb(nx, ny, cx, cy)
        d_opp = cheb(nx, ny, ox, oy)
        # Push toward center while not giving up too much pressure.
        return -d_center * 1.2 - d_opp * 0.4

    # Choose best move deterministically with stable tie-breaking.
    best_val = -10**18
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = score_move(nx, ny)
        if v > best_val + 1e-9:
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]