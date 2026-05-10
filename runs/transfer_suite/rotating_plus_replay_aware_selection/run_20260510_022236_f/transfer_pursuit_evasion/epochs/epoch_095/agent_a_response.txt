def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "escape", "flee"))
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if (sx, sy) == (ox, oy):
        return [0, 0]

    def cheb(x, y):
        dx = abs(ox - x)
        dy = abs(oy - y)
        return dx if dx > dy else dy

    def manh_to_obst(x, y):
        if not obstacles:
            return 99
        best = 99
        for px, py in obstacles:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    turn = int(observation.get("turn_index", 0) or 0)
    zig = 1 if (turn % 2 == 0) else -1

    best_move = (0, 0)
    best_val = -10**18 if is_evader else 10**18

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not legal(nx, ny):
            continue

        d = cheb(nx, ny)
        obst = manh_to_obst(nx, ny)
        corner_bias = abs(far_corner[0] - nx) + abs(far_corner[1] - ny)
        toward_dir = (abs(far_corner[0] - nx) < abs(far_corner[0] - sx)) or (abs(far_corner[1] - ny) < abs(far_corner[1] - sy))

        # Zigzag: if closer than average, try forcing orthogonal component alternation.
        zigterm = 0
        if dxm != 0 and dym != 0:
            zigterm = 0.4 * zig
        elif dxm == 0 and dym != 0:
            zigterm = 0.2 * zig
        elif dxm != 0 and dym == 0:
            zigterm = -0.2 * zig

        # Obstacle avoidance: prefer being farther from obstacles (especially for evader).
        if is_evader:
            val = d * 10.0 + corner_bias * (0.08 if toward_dir else 0.03) + (obst * 0.9) + zigterm
            if val > best_val:
                best_val = val
                best_move = (dxm, dym)
        else:
            # Pursuer: minimize distance, but don't run into obstacles; bias to reduce both axes.
            ax = 1 if abs(ox - nx) < abs(ox - sx) else -1
            ay = 1 if abs(oy - ny) < abs(oy - sy) else -1
            axis_gain = (ax + ay) * 0.7
            val = d * (-10.0) + axis_gain + (obst * 0.5) + zigterm
            if val < best_val:
                best_val = val
                best_move = (dxm, dym)

    dxm, dym = best_move
    if dxm not in (-1, 0, 1) or dym not in (-1, 0, 1):
        return [0, 0]
    return [dxm, dym]