def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    opp_role = (observation.get("opponent_role", "") or "").lower()
    opp_evader = ("evader" in opp_role) or ("runner" in opp_role)

    def neigh_obs(x, y):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0: 
                    continue
                if (x + ax, y + ay) in obstacles:
                    c += 1
        return c

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        base_dist = md(nx, ny, ox, oy)

        opp_best = None
        opp_best_val = None
        for odx, ody in moves:
            px, py = ox + odx, oy + ody
            if not free(px, py):
                px, py = ox, oy
            dist_after = md(nx, ny, px, py)
            val = -dist_after if opp_evader else dist_after
            if opp_best_val is None or (val > opp_best_val):
                opp_best_val = val
                opp_best = (px, py)

        if opp_best is None:
            opp_best = (ox, oy)

        px, py = opp_best
        final_dist = md(nx, ny, px, py)
        # pursuer wants small distance; add slight penalty near crowded obstacles
        my_score = (-final_dist * 10) - neigh_obs(nx, ny) + (0 if (dx == 0 and dy == 0) else 1)
        if my_score > best_score:
            best_score = my_score
            best_move = [dx, dy]

    return best_move