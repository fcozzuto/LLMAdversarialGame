def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources or w <= 0 or h <= 0:
        for dx, dy in sorted(dirs):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    best_rx, best_ry = resources[0][0], resources[0][1]
    best_val = -10**18
    for rx, ry in sorted(resources):
        dm = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        near_op = cheb(rx, ry, ox, oy)
        val = (do - dm) * 10 - dm - (10 - min(10, near_op))
        if val > best_val:
            best_val = val
            best_rx, best_ry = rx, ry

    tx, ty = best_rx, best_ry
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dmy = cheb(nx, ny, tx, ty)
        dmy2 = cheb(ox, oy, tx, ty)
        do_next = dmy2
        score = (do_next - dmy) * 10 - dmy
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]