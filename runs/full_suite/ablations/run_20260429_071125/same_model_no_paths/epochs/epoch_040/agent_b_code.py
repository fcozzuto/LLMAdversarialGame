def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    moves = [(dx, dy) for dx, dy in dirs if ok(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # Staying still is allowed; evaluate all moves similarly.
        if resources:
            my_d = cheb(nx, ny, ox, oy)  # closer to opponent often helps deny.
            # Choose target resource that maximizes advantage (reachability vs opponent).
            best_adv = -10**18
            for tx, ty in resources:
                d_me = cheb(nx, ny, tx, ty)
                d_op = cheb(ox, oy, tx, ty)
                # If we can reach sooner than opponent, strongly rewarded.
                adv = (d_op - d_me)
                # Small bias toward nearer resources and away from being stuck far from center late.
                adv -= 0.05 * d_me
                adv -= 0.02 * (abs(nx - cx) + abs(ny - cy))
                # Prefer moves that reduce immediate distance to the chosen resource.
                if adv > best_adv:
                    best_adv = adv
            # Combine: prioritize capture opportunity, then slight denial by reducing my distance to opponent.
            val = 100.0 * best_adv - 0.3 * my_d
        else:
            # No visible resources: drift toward center deterministically.
            val = -abs(nx - cx) - abs(ny - cy)
            # Slightly keep away from opponent to avoid accidental blocking.
            val -= 0.05 * cheb(nx, ny, ox, oy)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]