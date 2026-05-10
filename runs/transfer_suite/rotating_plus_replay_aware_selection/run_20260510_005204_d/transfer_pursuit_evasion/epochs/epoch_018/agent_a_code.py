def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("escape" in role) or ("hide" in role) or ("evader" in role)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    obs_list = list(blocked)
    def near_obs_pen(x, y):
        m = 10**9
        for bx, by in obs_list:
            d = cheb(x, y, bx, by)
            if d < m:
                m = d
        return m if m != 10**9 else 5

    best_move = [0, 0]
    best_val = -10**18 if is_evader else 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        corner_dist = cheb(nx, ny, target_corner[0], target_corner[1])
        nobs = near_obs_pen(nx, ny)

        if is_evader:
            val = dist + 0.25 * corner_dist + 0.05 * nobs
        else:
            val = -dist - 0.05 * (5 - nobs) - 0.01 * corner_dist  # tiny bias to keep distance tradeoffs

        if is_evader:
            if val > best_val or (val == best_val and [dx, dy] < best_move):
                best_val, best_move = val, [dx, dy]
        else:
            if val < best_val or (val == best_val and [dx, dy] < best_move):
                best_val, best_move = val, [dx, dy]

    return best_move