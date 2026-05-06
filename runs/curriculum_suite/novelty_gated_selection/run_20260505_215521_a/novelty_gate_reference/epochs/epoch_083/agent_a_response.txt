def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        best_val = None
        for tx, ty in resources:
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            val = (sd - od) * 10 + sd  # smaller is better: we want resources we are closer to than opponent
            if best is None or val < best_val or (val == best_val and (od > cheb(ox, oy, best[0], best[1]) or sd < cheb(sx, sy, best[0], best[1]))):
                best = (tx, ty)
                best_val = val
        tx, ty = best

        best_move = (0, 0)
        best_m = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            nd = cheb(nx, ny, tx, ty)
            oppd = cheb(nx, ny, ox, oy)
            # primary: minimize distance to target, secondary: maximize separation from opponent
            m = (nd, -oppd, abs(dx) + abs(dy), dx, dy)
            if best_m is None or m < best_m:
                best_m = m
                best_move = (dx, dy)
        dx, dy = best_move
        return [dx, dy]

    # No visible resources: drift toward center while avoiding the opponent
    cx, cy = w // 2, h // 2
    best_move = (0, 0)
    best_m = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        cd = cheb(nx, ny, cx, cy)
        oppd = cheb(nx, ny, ox, oy)
        m = (cd, -oppd, abs(dx) + abs(dy), dx, dy)
        if best_m is None or m < best_m:
            best_m = m
            best_move = (dx, dy)
    dx, dy = best_move
    return [dx, dy]