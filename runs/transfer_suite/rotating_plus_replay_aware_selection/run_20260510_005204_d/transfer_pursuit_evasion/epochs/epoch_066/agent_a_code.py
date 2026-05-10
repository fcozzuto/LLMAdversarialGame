def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    we_evader = ("evader" in role) or ("runner" in role)
    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    def near_obst_cnt(x, y):
        c = 0
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if (x + i, y + j) in blocked:
                    c += 1
        return c

    def wall_dist(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    cur_d = cheb(sx, sy, ox, oy)
    opp_d_wall = wall_dist(ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            score = -10**9 if we_evader else 10**9
        else:
            d = cheb(nx, ny, ox, oy)
            if we_evader:
                # Maximize separation; avoid getting boxed in near obstacles/walls.
                wall_pen = -2.0 * (4 - wall_dist(nx, ny))  # closer to wall => worse
                obst_pen = -1.2 * near_obst_cnt(nx, ny)
                # If opponent is near a wall, favor moving away from that wall to prevent trapping.
                opp_wall_drive = 0.0
                if opp_d_wall <= 1:
                    if ox == 0:
                        opp_wall_drive = 1.4 if nx > sx else -1.4
                    elif ox == w - 1:
                        opp_wall_drive = 1.4 if nx < sx else -1.4
                    if oy == 0:
                        opp_wall_drive += 1.0 if ny > sy else -1.0
                    elif oy == h - 1:
                        opp_wall_drive += 1.0 if ny < sy else -1.0
                score = (d - cur_d) * 2.5 + d * 0.85 + wall_pen + obst_pen + opp_wall_drive
            else:
                # Pursuer: minimize distance; avoid obstacles; also prefer moving into open space.
                d_term = (cur_d - d) * 3.0 + (-d) * 0.9
                obst_pen = -2.0 * near_obst_cnt(nx, ny)
                open_bonus = 0.6 * wall_dist(nx, ny)
                score = d_term + obst_pen + open_bonus

        if best is None or (score > best_score) or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]