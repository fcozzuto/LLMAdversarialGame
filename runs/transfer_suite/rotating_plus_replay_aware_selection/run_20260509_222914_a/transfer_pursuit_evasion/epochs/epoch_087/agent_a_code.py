def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def valid(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: man(c[0], c[1], ox, oy))

    def obstacle_clearance(x, y):
        # Prefer staying away from obstacles (deterministic local score)
        if not obstacles:
            return 2
        best = 99
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    return 0
                best = min(best, abs(nx - x) + abs(ny - y))
        return 1 if best == 1 else 2

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = man(nx, ny, ox, oy)
        clr = obstacle_clearance(nx, ny)

        if is_evader:
            # maximize distance and also pull toward farthest corner from pursuer
            corner_bias = man(nx, ny, far_corner[0], far_corner[1])
            # higher is better; corner_bias lower means closer, but we want to be closer to far corner => use negative
            val = (d * 10) + (clr * 2) - corner_bias
            better = (best_val is None) or (val > best_val) or (val == best_val and (dx, dy) < (best_move[0], best_move[1]))
        else:
            # pursuer: minimize distance; if tied, improve corner-to-corner pressure by moving toward opponent's side
            val = (-d * 10) + (clr * 2) - man(nx, ny, far_corner[0], far_corner[1]) * 0.01
            better = (best_val is None) or (val > best_val) or (val == best_val and (dx, dy) < (best_move[0], best_move[1]))

        if better:
            best_val = val
            best_move = [dx, dy]

    return best_move