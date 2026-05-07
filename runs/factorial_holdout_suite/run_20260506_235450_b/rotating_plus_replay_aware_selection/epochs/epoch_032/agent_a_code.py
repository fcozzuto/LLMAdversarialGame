def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy, nx, ny))
    if not legal or not resources:
        return [0, 0]

    # Choose move that maximizes immediate advantage: can we secure a resource sooner than opponent?
    best_move = legal[0]
    best_val = None
    for dx, dy, nx, ny in legal:
        best_res_val = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Secure win if ds < do; otherwise still chase but prefer least overrun and closeness
            secure_flag = 1 if ds < do else 0
            val = (secure_flag, do - ds, -ds, - (abs(nx - ox) + abs(ny - oy)))
            if best_res_val is None or val > best_res_val:
                best_res_val = val
        if best_val is None or best_res_val > best_val:
            best_val = best_res_val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]