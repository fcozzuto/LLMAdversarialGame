def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def eval_pos(px, py):
        if not resources:
            return -cheb(px, py, ox, oy)
        best = -10**18
        for (rx, ry) in resources:
            d_me = cheb(px, py, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Prefer resources you can beat and collect sooner; also discourage being closer to opponent than you are.
            score = (d_opp - d_me) * 20 - d_me
            # If you step adjacent/onto opponent, heavily penalize.
            if cheb(px, py, ox, oy) <= 1:
                score -= 80
            if (rx, ry) == (px, py):
                score += 1000
            if score > best:
                best = score
        # Small tie-breaker: move toward the "best" region from current position.
        best -= cheb(px, py, ox, oy) * 2
        return best

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        val = eval_pos(nx, ny)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]