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

    def md(x1, y1, x2, y2):
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

    # Prefer moves that immediately grab (if present), else maximize (opponent delay) while heading toward resources.
    best_move = None
    best_val = None
    target_order = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) == (sx, sy):
            target_order = [(rx, ry)]
            break
        target_order.append((rx, ry))
    if not target_order:
        target_order = [(int(r[0]), int(r[1])) for r in resources]

    for dx, dy, nx, ny in legal:
        # If we can collect this turn, do it.
        if (nx, ny) in target_order:
            return [dx, dy]

        self_adv = []
        for rx, ry in target_order:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            # Higher means more likely we secure before opponent.
            val = (do - ds) * 100 - ds
            self_adv.append(val)
        if self_adv:
            score = max(self_adv)
        else:
            score = -md(nx, ny, ox, oy)

        # Small deterministic bias: prioritize decreasing distance to opponent if we're behind, else toward middle.
        center = (w // 2, h // 2)
        bias = -md(nx, ny, center[0], center[1]) * 0.001 - md(nx, ny, ox, oy) * 0.0001
        score = score + bias

        # Deterministic tie-break by (dx,dy) order in moves list.
        if best_val is None or score > best_val:
            best_val = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]