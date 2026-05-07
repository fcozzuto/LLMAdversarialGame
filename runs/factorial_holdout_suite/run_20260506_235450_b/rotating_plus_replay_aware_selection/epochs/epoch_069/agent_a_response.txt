def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    legal_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in legal_moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal or not resources:
        return [0, 0]

    best = None
    for dx, dy, nx, ny in legal:
        best_for_move = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            dself = cheb(nx, ny, rx, ry)
            dopp = cheb(ox, oy, rx, ry)
            adv = dopp - dself
            # Prefer securing/denying (max advantage), then quick self progress, then farther from opponent.
            key = (adv, -dself, -dopp)
            if best_for_move is None or key > best_for_move:
                best_for_move = key
        move_key = (best_for_move[0], best_for_move[1], best_for_move[2], -abs(dx), -abs(dy), -dx, -dy, 0)
        if best is None or move_key > best:
            best = move_key
            best_move = [dx, dy]

    if not best:
        return [0, 0]
    return best_move