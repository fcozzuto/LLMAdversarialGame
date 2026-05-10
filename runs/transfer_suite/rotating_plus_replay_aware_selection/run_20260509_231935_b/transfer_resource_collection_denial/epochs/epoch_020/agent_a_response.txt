def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))
    best_move = (0, 0)
    best_val = -10**18

    def eval_pos(nx, ny):
        if (nx, ny) in obstacles:
            return -10**18
        if not resources:
            cx, cy = w // 2, h // 2
            return -dist8(nx, ny, cx, cy) + 0.6 * dist8(nx, ny, ox, oy)
        best = -10**18
        for rx, ry in resources:
            md = dist8(nx, ny, rx, ry)
            od = dist8(ox, oy, rx, ry)
            adv = od - md  # positive if we are closer
            # Strongly prefer moves that create guaranteed advantage; break ties by closeness.
            val = (adv * 12) - (md * 1.1)
            if adv == 0:
                val -= dist8(nx, ny, ox, oy) * 0.15
            if rx == nx and ry == ny:
                val += 500  # immediate pickup if visible
            if val > best:
                best = val
        return best

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        v = eval_pos(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]