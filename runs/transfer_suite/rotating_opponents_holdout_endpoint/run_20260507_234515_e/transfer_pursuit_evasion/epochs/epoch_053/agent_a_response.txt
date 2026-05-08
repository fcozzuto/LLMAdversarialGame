def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in oset

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def is_evader(role):
        return ("evad" in role) or ("evasion" in role)

    self_is_evader = is_evader(self_role)
    opp_is_evader = is_evader(opp_role)
    if not self_role:
        self_is_evader = False

    # Evader: move to maximize distance from pursuer (opponent assumed pursuer)
    if self_is_evader:
        best = None
        best_d = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist(nx, ny, ox, oy)
            # small preference to reduce risk of moving into obstacle-adjacent chokepoints
            score = d * 10 - (0 if (nx, ny) not in oset else 1000)
            if score > best_d:
                best_d = score
                best = (nx, ny)
        if best is None:
            return [0, 0]
        return [best[0] - sx, best[1] - sy]

    # Pursuer: choose move that minimizes next distance, with opponent best-response prediction
    best_move = (0, 0)
    best_score = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Predict opponent response: evader maximizes distance, pursuer minimizes
        bo = None
        bval = -10**18 if opp_is_evader else 10**18
        for odx, ody in moves:
            mx, my = ox + odx, oy + ody
            if not valid(mx, my):
                continue
            d = dist(mx, my, nx, ny)
            if opp_is_evader:
                val = d
                if val > bval:
                    bval = val
                    bo = (mx, my)
            else:
                val = -d
                if val > bval:
                    bval = val
                    bo = (mx, my)
        if bo is None:
            bo = (ox, oy)
        # Goal: reach exact capture cell; tie-break by stronger progress and slight center bias
        capture = 0 if (nx == bo[0] and ny == bo[1]) else 1
        centerx, centery = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = abs(nx - centerx) + abs(ny - centery)
        score = capture * 10**6 + dist(nx, ny, bo[0], bo[1]) * 10 + center_bias
        if score < best_score:
            best_score = score
            best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]