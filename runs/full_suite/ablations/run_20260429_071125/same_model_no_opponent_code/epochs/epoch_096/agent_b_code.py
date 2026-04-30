def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def eval_pos(x, y):
        if not resources:
            return -cheb(x, y, (w - 1), 0) * 0.01
        best = -10**9
        for rx, ry in resources:
            d_self = cheb(x, y, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent, and slightly prefer closeness overall
            score = (d_opp - d_self) * 10 - d_self
            # Penalize being "aligned" with an obstacle corner nearby (soft local detour)
            if (rx - 1, ry) in obstacles or (rx + 1, ry) in obstacles or (rx, ry - 1) in obstacles or (rx, ry + 1) in obstacles:
                score -= 0.5
            if score > best:
                best = score
        return best

    best_move = (0, 0)
    best_val = -10**18
    # Deterministic tie-breaking order: dirs as listed
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            v = eval_pos(nx, ny)
            # If values are equal, keep earlier move in dirs by not updating on ties
            if v > best_val:
                best_val = v
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]