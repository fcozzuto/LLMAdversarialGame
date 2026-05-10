def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def is_evader(role):
        r = (role or "").lower()
        return ("evader" in r) or ("runner" in r) or ("evasion" in r) or ("evasive" in r)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    self_evade = is_evader(observation.get("self_role"))

    # Wall-run/Wall-avoid bias: prefer staying near a boundary if evading, avoid if pursuing.
    boundaries = {0, w - 1, 0, h - 1}
    best_move = [0, 0]
    best_key = None

    cur_dx = ox - sx
    cur_dy = oy - sy
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not valid(nx, ny):
            continue
        dist = man(nx, ny, ox, oy)

        # Heuristic: pursue by closing on the larger axis; evade by maximizing distance.
        adx = abs(ox - nx)
        ady = abs(oy - ny)
        major = max(adx, ady)

        # Boundary preference
        near_left = nx == 0
        near_right = nx == w - 1
        near_top = ny == 0
        near_bottom = ny == h - 1
        near_boundary = 1 if (near_left or near_right or near_top or near_bottom) else 0

        # Obstacle pressure: count adjacent obstacle cells (prefer fewer when pursuing, more when evading).
        adj_obs = 0
        for ax, ay in dirs:
            tx, ty = nx + ax, ny + ay
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                adj_obs += 1

        # Tie-breaker: bias towards aligning diagonally when possible.
        align = 0
        if (cur_dx == 0 and ddy != 0) or (cur_dy == 0 and ddx != 0):
            align = 1
        if (cur_dx != 0 and cur_dy != 0 and ddx != 0 and ddy != 0):
            align = 1

        # Compose score key
        if self_evade:
            # maximize distance, then prefer boundary (wall-run), then reduce major alignment (harder to intercept), then more obstacle-adjacency
            key = (-dist, -near_boundary, major, -adj_obs, -align)
        else:
            # minimize distance, then prefer moving towards the larger axis reduction, then avoid obstacles, then prefer alignment
            # major_after smaller is better
            key = (dist, major, adj_obs, -align)

        if best_key is None or key < best_key:
            best_key = key
            best_move = [ddx, ddy]

    return best_move