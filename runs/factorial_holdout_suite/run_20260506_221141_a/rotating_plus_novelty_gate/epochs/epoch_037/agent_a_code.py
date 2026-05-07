def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if not resources:
        return [0, 0]
    if (sx, sy) in set(resources):
        return [0, 0]

    def cheb_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = None
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in blocked:
            continue
        # Score this move by the best target it lets us "beat" the opponent on.
        move_best = None
        for rx, ry in resources:
            sd = cheb_dist(nx, ny, rx, ry)
            od = cheb_dist(ox, oy, rx, ry)
            advantage = od - sd
            # Strongly prefer targets where we can arrive no later than opponent.
            s = (advantage, -sd, -(abs(ox - nx) + abs(oy - ny)))
            if move_best is None or s > move_best:
                move_best = s
        if move_best is None:
            continue
        if best is None or move_best > best:
            best = move_best
            best_move = [dx, dy]

    return best_move