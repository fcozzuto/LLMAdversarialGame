def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # deterministic drift toward center while keeping away from obstacles
        tx, ty = w // 2, h // 2
        best = None
        bestd = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if bestd is None or d < bestd:
                bestd = d
                best = [dx, dy]
        return best if best is not None else [0, 0]

    # Evaluation: prefer immediate capture, then resources where we are closer than opponent; penalize letting opponent be closer.
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if (nx, ny) in set(resources):
            val = 10_000 + cheb(nx, ny, ox, oy)
        else:
            val = -10**9
            for rx, ry in resources:
                ourd = cheb(nx, ny, rx, ry)
                oppd = cheb(ox, oy, rx, ry)
                # Bigger is better: our advantage over opponent to that resource; also slightly favor nearer resources overall.
                score = (oppd - ourd) * 10 - ourd
                # Discourage moves that get us too close to obstacle-less traps only via distance; keep simple.
                if score > val:
                    val = score

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move