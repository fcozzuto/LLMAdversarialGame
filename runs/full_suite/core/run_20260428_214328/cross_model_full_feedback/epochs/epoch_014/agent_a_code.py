def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obs

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(nx, ny):
        return inside(nx, ny) and not blocked(nx, ny)

    my_pos = (sx, sy)
    opp_pos = (ox, oy)
    opp_dist_now = dist(my_pos, opp_pos)

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myn = (nx, ny)
        if res:
            best_diff = -10**9
            best_r_dist = 10**9
            for rx, ry in res:
                r = (rx, ry)
                sd = dist(myn, r)
                od = dist(opp_pos, r)
                diff = od - sd  # positive if we are closer than opponent
                if diff > best_diff or (diff == best_diff and sd < best_r_dist):
                    best_diff, best_r_dist = diff, sd
            if best_diff == -10**9:
                continue
            # Encourage contesting closer-to-resources, while not walking away from opponent too much.
            val = best_diff * 10 - best_r_dist + (opp_dist_now - dist(myn, opp_pos)) * 0.3
        else:
            # No resources: move toward opponent cautiously but avoid getting trapped on obstacles.
            val = (opp_dist_now - dist(myn, opp_pos)) * 2
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    if valid(sx, sy):
        return [int(best_move[0]), int(best_move[1])]
    # If current cell is somehow invalid, choose any valid move deterministically.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [int(dx), int(dy)]
    return [0, 0]