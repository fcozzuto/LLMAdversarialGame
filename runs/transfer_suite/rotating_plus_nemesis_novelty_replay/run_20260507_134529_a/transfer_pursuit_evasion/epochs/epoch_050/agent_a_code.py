def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def clamp_ok(x, y):
        return (x, y) if inb(x, y) else (sx, sy)

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    role = (observation.get("self_role") or "").lower()
    self_is_evader = "evader" in role

    def mobility(x, y, occ_obstacles=obstacles):
        m = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in occ_obstacles:
                m += 1
        return m

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = clamp_ok(sx + dx, sy + dy)
        if nx == sx and ny == sy and (dx, dy) != (0, 0):
            continue

        d2 = dist(nx, ny, ox, oy)
        my_mob = mobility(nx, ny)

        # one-step lookahead: estimate opponent response by considering their best option
        opp_best_d2 = None
        opp_best_mob = -1
        for odx, ody in moves:
            tx, ty = sx, sy  # unused, keep deterministic
            onx, ony = ox + odx, oy + ody
            if not inb(onx, ony):
                onx, ony = ox, oy
            od2 = dist(nx, ny, onx, ony)
            om = mobility(onx, ony)
            if opp_best_d2 is None:
                opp_best_d2, opp_best_mob = od2, om
            else:
                if self_is_evader:
                    # opponent is pursuer: minimize distance; tie-break by minimizing evader mobility pressure
                    if od2 < opp_best_d2 or (od2 == opp_best_d2 and om > opp_best_mob):
                        opp_best_d2, opp_best_mob = od2, om
                else:
                    # opponent is evader: maximize distance; tie-break by maximizing their mobility
                    if od2 > opp_best_d2 or (od2 == opp_best_d2 and om > opp_best_mob):
                        opp_best_d2, opp_best_mob = od2, om

        if opp_best_d2 is None:
            opp_best_d2 = d2
            opp_best_mob = mobility(ox, oy)

        # score shaping
        if self_is_evader:
            # survive: maximize distance; avoid low mobility; avoid letting pursuer get too close
            corner_pen = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)
            val = (opp_best_d2 * 2.0) + (my_mob * 0.5) + (corner_pen * 0.05)
        else:
            # pursue: minimize predicted distance; reduce opponent mobility; prefer blocking corners (faster capture path)
            corner_bonus = (min(ox, w - 1 - ox) + min(oy, h - 1 - oy)) * -0.01
            val = (-opp_best_d2 * 2.0) + (opp_best_mob * -0.4) + corner_bonus

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]