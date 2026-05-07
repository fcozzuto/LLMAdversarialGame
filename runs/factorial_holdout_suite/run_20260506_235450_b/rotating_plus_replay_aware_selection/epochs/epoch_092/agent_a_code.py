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

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    res_cells = [(int(r[0]), int(r[1])) for r in resources if len(r) >= 2]
    best_move = (0, 0, sx, sy)
    best_val = None

    for dx, dy, nx, ny in legal:
        self_best = -10**9
        for rx, ry in res_cells:
            s_d = dist(nx, ny, rx, ry)
            o_d = dist(ox, oy, rx, ry)
            adv = o_d - s_d  # positive means we can reach earlier/equal advantage
            val = adv * 6 - s_d  # prioritize resources we can secure
            if (nx == rx and ny == ry):
                val += 1000  # immediate pickup
            self_best = val if val > self_best else self_best
        # Mild preference to keep heading toward center to avoid getting stuck
        center_bias = -(abs((nx - (w - 1) / 2)) + abs((ny - (h - 1) / 2))) * 0.01
        total = self_best + center_bias
        if best_val is None or total > best_val:
            best_val = total
            best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]