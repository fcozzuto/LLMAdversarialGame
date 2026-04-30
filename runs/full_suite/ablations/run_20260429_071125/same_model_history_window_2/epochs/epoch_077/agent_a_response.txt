def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obstacle_dist(x, y):
        if not obstacles:
            return 10
        best = 10
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < best:
                best = d
        return best

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                moves.append((dx, dy))
    if not resources or any(x == sx and y == sy for (x, y) in resources):
        return [0, 0]
    moves.sort()  # deterministic tie-break

    # Evaluate each move by how well it positions us vs the opponent for the best contested resource.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        od = obstacle_dist(nx, ny)
        local_best = None
        for rx, ry in resources:
            d_us = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Bias: take resources we can reach meaningfully earlier; if behind, prefer reducing that gap.
            gap = d_op - d_us
            score = gap * 120 - d_us * 6
            # Small bias to finish closer when gaps are similar
            if d_op <= d_us:
                score += 25 - (d_us - d_op) * 10
            if local_best is None or score > local_best:
                local_best = score
        total = local_best + od * 2 + (-(abs(nx - sx) + abs(ny - sy))) * 0.01
        if best_score is None or total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]