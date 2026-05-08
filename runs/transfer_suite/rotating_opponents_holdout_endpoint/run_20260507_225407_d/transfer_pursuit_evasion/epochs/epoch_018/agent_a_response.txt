def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is None:
            continue
        x, y = p
        obstacles.add((int(x), int(y)))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    role = (observation.get("self_role") or "").lower()
    dx_line = ox - sx
    dy_line = oy - sy

    # Detect a "wall" blocking straight line between us and opponent along x or y.
    blocked = 0
    if sx == ox:
        x = sx
        y0, y1 = sorted([sy, oy])
        for (bx, by) in obstacles:
            if bx == x and y0 < by < y1:
                blocked += 1
    if sy == oy:
        y = sy
        x0, x1 = sorted([sx, ox])
        for (bx, by) in obstacles:
            if by == y and x0 < bx < x1:
                blocked += 1
    need_detour = blocked > 0

    # Prefer avoiding cells adjacent to obstacles to reduce "wall-running" exploitation.
    def obstacle_proximity(x, y):
        c = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                if (x + ex, y + ey) in obstacles:
                    c += 1
        return c

    best = None
    best_move = (0, 0)

    for dxx, dyy in dirs:
        nx, ny = sx + dxx, sy + dyy
        if not valid(nx, ny):
            continue
        md_after = abs(ox - nx) + abs(oy - ny)
        sd_after = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
        prox = obstacle_proximity(nx, ny)

        # If blocked on a straight line, penalize moves that keep the same x or y alignment.
        align_pen = 0
        if need_detour:
            if nx == ox or ny == oy:
                align_pen = 6

        # If moving diagonally doesn't help under block, discourage useless alignment.
        dx_change = abs((ox - nx) - (ox - sx))
        dy_change = abs((oy - ny) - (oy - sy))

        if role == "pursuer":
            score = (md_after, sd_after, prox + align_pen, -dx_change - dy_change)
        else:  # evader behavior
            score = (-md_after, -sd_after, prox + align_pen, dx_change + dy_change)

        if best is None or score < best:
            best = score
            best_move = (dxx, dyy)

    return [int(best_move[0]), int(best_move[1])]