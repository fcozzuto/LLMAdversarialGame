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
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0)]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx != 0 or dy != 0:
                if inb(sx + dx, sy + dy):
                    moves.append((dx, dy))
    if not moves:
        return [0, 0]

    best_move = (0, 0)
    best_score = None
    best_tie = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        opp_shadow = cheb(ox, oy, nx, ny)
        local_best = -10**9
        local_best_d = 10**9
        local_best_cell = None
        for rx, ry in resources:
            dself = cheb(nx, ny, rx, ry)
            dopp = cheb(ox, oy, rx, ry)
            if dself == 0:
                value = 1000
            else:
                value = (dopp - dself) * 10 - dself
                if dself <= dopp:
                    value += 25 - dself
                value -= 0.6 * opp_shadow  # avoid running into opponent radius
            if value > local_best or (value == local_best and dself < local_best_d):
                local_best = value
                local_best_d = dself
                local_best_cell = (rx, ry)
        # deterministic tie-break: prefer smaller d to chosen cell, then smaller move lexicographically
        tie = (local_best_d, local_best_cell[0], local_best_cell[1], dx, dy)
        if best_score is None or local_best > best_score or (local_best == best_score and tie < best_tie):
            best_score = local_best
            best_tie = tie
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]