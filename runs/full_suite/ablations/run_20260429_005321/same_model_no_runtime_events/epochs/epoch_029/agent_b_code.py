def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    res_set = set(resources)

    # Choose moves that improve relative reachability of resources vs opponent.
    best_move = (0, 0)
    best_val = -10**9
    for dx, dy, nx, ny in legal:
        # If we land on a resource, take it decisively.
        if (nx, ny) in res_set:
            val = 10**6
        else:
            val = -cheb(nx, ny, ox, oy) * 0.02  # mild "kite" away from opponent

            # Evaluate best target by relative distance advantage.
            best_adv = -10**9
            for tx, ty in resources:
                ds = cheb(nx, ny, tx, ty)
                do = cheb(ox, oy, tx, ty)
                adv = do - ds  # positive means we can reach sooner
                # Prefer closer absolute reach too, but mainly improve advantage.
                score = adv * 10 - ds
                if score > best_adv:
                    best_adv = score
            if resources:
                val += best_adv
            else:
                # No visible resources: move toward opponent's corner mirror to keep pressure.
                val += -(cheb(nx, ny, w - 1, h - 1) if (sx, sy) == (0, 0) else cheb(nx, ny, 0, 0)) * 0.01

            # Small tie-break: reduce distance to nearest resource from current position to avoid oscillation.
            if resources:
                ds0 = 10**9
                for tx, ty in resources:
                    d0 = cheb(sx, sy, tx, ty)
                    if d0 < ds0:
                        ds0 = d0
                d1 = 10**9
                for tx, ty in resources:
                    d1 = min(d1, cheb(nx, ny, tx, ty))
                val += (ds0 - d1) * 1.5

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]