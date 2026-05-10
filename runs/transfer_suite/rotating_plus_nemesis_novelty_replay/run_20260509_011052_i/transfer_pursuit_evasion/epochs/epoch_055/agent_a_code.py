def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in self_role) and ("evader" not in self_role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Predict opponent next position by one greedy step towards/away from us.
    # If we are pursuer, opponent is evader; assume it moves to maximize its distance from us.
    # If we are evader, opponent is pursuer; assume it moves to minimize its distance to us.
    best_opp = (ox, oy)
    best_score = -10**9 if pursuer else 10**9
    for adx, ady in dirs:
        nx, ny = ox + adx, oy + ady
        if not valid(nx, ny): 
            continue
        d = cheb(nx, ny, sx, sy)
        sc = d if pursuer else -d
        if sc > best_score:
            best_score = sc
            best_opp = (nx, ny)
    px, py = best_opp

    # Evaluate our moves with a strong chase/cutoff objective and obstacle-safe preference.
    # Also bias toward moves that reduce distance to predicted position (pursuer) or increase it (evader).
    def mobility(x, y):
        m = 0
        for dx, dy in dirs:
            if valid(x + dx, y + dy):
                m += 1
        return m

    # Tie-breaker: prefer staying on the same cheb-level for pursuer (more stable pursuit),
    # and prefer increasing cheb distance for evader (more stable evasion).
    want = -1 if pursuer else 1
    best_move = (0, 0)
    best_val = -10**18 if pursuer else 10**18
    cur_d = cheb(sx, sy, px, py)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d1 = cheb(nx, ny, px, py)
        dopp = cheb(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        # pursuer: minimize predicted distance and keep opponent close by also reducing current distance slightly
        # evader: maximize predicted distance; if far, also keep own mobility high.
        base = -d1 if pursuer else d1
        stab = -(abs(dopp - cur_d)) if pursuer else -(abs(dopp - cur_d))
        val = base * 1000 + mob * (1 if pursuer else 3) + stab
        if pursuer:
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        else:
            if val < best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]