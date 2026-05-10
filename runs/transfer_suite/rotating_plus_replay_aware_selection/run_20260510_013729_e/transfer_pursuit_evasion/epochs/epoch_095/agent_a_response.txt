def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_ev = ("evad" in self_role) or ("run" in self_role) or ("escap" in self_role)
    opp_ev = ("evad" in opp_role) or ("run" in opp_role) or ("escap" in opp_role)
    act_as_evader = self_ev or (not opp_ev and ("evad" not in self_role and "run" not in self_role and "escap" not in self_role) and (self_role == ""))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Candidate move order biases diagonal + horizontal/vertical ties for stability
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1),(0,0)]

    best_score = None
    best_move = [0, 0]
    # If we are evader: maximize distance; otherwise: minimize distance
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny): 
            continue
        if (nx, ny) in obs:
            continue
        d = cheb(nx, ny, ox, oy)
        # Pursuer strongly prefers smaller chebyshev distance; evader prefers larger
        score = -d if not act_as_evader else d
        # Deterministic tie-break: prefer moves that progress in x then y toward goal
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            # tie-break: closer alignment to target direction
            cur1 = abs((sx + best_move[0]) - ox) + abs((sy + best_move[1]) - oy)
            cur2 = abs(nx - ox) + abs(ny - oy)
            if act_as_evader:
                if cur2 > cur1:
                    best_move = [dx, dy]
            else:
                if cur2 < cur1:
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]