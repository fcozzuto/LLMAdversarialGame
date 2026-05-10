def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_ev = ("evader" in self_role) or ("evasion" in self_role) or ("runner" in self_role)
    opp_ev = ("evader" in opp_role) or ("evasion" in opp_role) or ("runner" in opp_role)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal_from(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return x, y
        return nx, ny

    my_goal = (lambda d: d) if self_ev else (lambda d: -d)  # evader maximizes distance; pursuer minimizes
    best_val = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = legal_from(sx, sy, dx, dy)
        if (nx, ny) == (ox, oy):
            val = -10**6 if self_ev else 10**6
        else:
            # opponent step prediction: greedily move based on its role
            best_opp = None
            for odx, ody in moves:
                tx, ty = legal_from(ox, oy, odx, ody)
                if (tx, ty) == (nx, ny):
                    opp_val = (-10**6 if opp_ev else 10**6)  # from our perspective
                else:
                    d = dist((nx, ny), (tx, ty))
                    opp_val = (d if opp_ev else -d)
                if best_opp is None or (opp_ev and opp_val > best_opp) or ((not opp_ev) and opp_val < best_opp):
                    best_opp = opp_val
            # from our perspective: if we're evader, we want maximize predicted distance; else minimize distance
            cur_d = dist((nx, ny), (ox, oy))
            val = (best_opp if self_ev else -best_opp) + my_goal(cur_d) * 0.01
        if best_val is None or (self_ev and val > best_val) or ((not self_ev) and val > best_val):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]