def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if resources:
        best_r = None
        best_d = 10**9
        best_t = 10**9
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # prefer resources closer to self; break ties by less advantage to opponent, then position
            t = (d, d - od, rx, ry)
            if t < (best_d, best_t, 10**9, 10**9) and d >= 0:
                best_r = (rx, ry)
                best_d = d
                best_t = d - od
        tx, ty = best_r
    else:
        tx, ty = w // 2, h // 2

    best_move = None
    best_score = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # small penalty for moving away from opponent to avoid getting trapped
        od = cheb(nx, ny, ox, oy)
        score = (d, -od, dx, dy)
        if score < best_score:
            best_score = score
            best_move = [dx, dy]

    if best_move is not None:
        return best_move
    # if all blocked, stay if possible; otherwise first valid direction
    if valid(sx, sy):
        return [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
    return [0, 0]