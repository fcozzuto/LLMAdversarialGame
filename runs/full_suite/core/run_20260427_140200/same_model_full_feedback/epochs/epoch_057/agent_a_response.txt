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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # If no resources: go to a deterministic target that pressures center and avoids being trapped.
    if not resources:
        tx, ty = (w // 2), (h // 2)
        mx = sx + (1 if tx > sx else -1 if tx < sx else 0)
        my = sy + (1 if ty > sy else -1 if ty < sy else 0)
        tx, ty = mx, my
        best = None
        for i, (dx, dy) in enumerate(dirs):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            score = (d, i)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]] if best is not None else [0, 0]

    # Choose move by racing: prefer resources where self is closer than opponent.
    # Also slightly avoid stepping next to obstacles.
    def eval_from(nsx, nsy):
        best = None
        for i, (rx, ry) in enumerate(resources):
            ds = cheb(nsx, nsy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Lower is better: (ds - do) captures race advantage.
            score = (ds - do, ds + do * 0, i)
            if best is None or score < best:
                best = score
        return best

    best_move = None
    for k, (dx, dy) in enumerate(dirs):
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        base = eval_from(nx, ny)
        # Obstacle proximity penalty (deterministic small tie-break).
        adj = 0
        for px in (-1, 0, 1):
            for py in (-1, 0, 1):
                if px == 0 and py == 0:
                    continue
                ax, ay = nx + px, ny + py
                if (ax, ay) in obstacles:
                    adj += 1
        score = (base[0], base[1], base[2], adj, k)
        if best_move is None or score < best_move[0]:
            best_move = (score, dx, dy)

    return [best_move[1], best_move[2]] if best_move is not None else [0, 0]