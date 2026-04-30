def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

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

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def obstacle_prox(x, y):
        if not obstacles:
            return 0
        best = 10**9
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    def pick_target():
        if not resources:
            return None
        best_r = resources[0]
        best_s = -10**18
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prioritize resources where we can be the first (or are closer than opponent).
            s = (od - sd)
            # Small bias toward nearer resources to avoid dithering.
            s += 0.05 * (7 - sd)
            best_r, best_s = (rx, ry, best_s) if s <= best_s else (rx, ry, s)
        return best_r

    tx = ty = None
    if resources:
        tx, ty = pick_target()

    legal_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            legal_moves.append((dx, dy, nx, ny))
    if not legal_moves:
        return [0, 0]

    if tx is None:
        # Obstacle-avoiding roam toward center deterministically.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-10**18, 0, 0)
        for dx, dy, nx, ny in legal_moves:
            score = -cheb(nx, ny, cx, cy) - 0.6 * obstacle_prox(nx, ny)
            if score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    best_score = -10**18
    best_dx, best_dy = 0, 0
    for dx, dy, nx, ny in legal_moves:
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # After moving, reduce our distance and also make it harder for opponent to convert.
        score = (od - sd)
        # Directly reward getting closer to target.
        score += 2.0 * (cheb(sx, sy, tx, ty) - sd)
        # Keep away from obstacles.
        score -= 0.9 / (1 + obstacle_prox(nx, ny))
        # Slight tie-break: prefer moves that don't increase distance to opponent target.
        score += 0.01 * (nx - sx) + 0.005 * (ny - sy)
        if score > best_score:
            best_score, best_dx, best_dy = score, dx, dy

    return [int(best_dx), int(best_dy)]