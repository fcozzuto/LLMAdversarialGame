def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) and ("evader" not in role)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def legal(px, py):
        res = []
        for dx, dy in dirs:
            nx, ny = px + dx, py + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                res.append((nx, ny, dx, dy))
        return res

    my_moves = legal(sx, sy)
    if not my_moves:
        return [0, 0]

    if not is_pursuer:
        # Evade: maximize distance.
        best = my_moves[0]
        best_d = cheb(best[0], best[1], ox, oy)
        for nx, ny, dx, dy in my_moves[1:]:
            d = cheb(nx, ny, ox, oy)
            if d > best_d:
                best_d = d
                best = (nx, ny, dx, dy)
        return [best[2], best[3]]

    # Pursuer: predict opponent's next move (assume it maximizes distance from us).
    opp_moves = legal(ox, oy)
    pred = opp_moves[0]
    pred_d = -1
    for nx, ny, _, _ in opp_moves:
        d = cheb(nx, ny, sx, sy)
        if d > pred_d:
            pred_d = d
            pred = (nx, ny, 0, 0)
    px, py = pred[0], pred[1]

    # Move to minimize distance to predicted position; break ties by also reducing current distance to actual opponent.
    best = my_moves[0]
    best_score = cheb(best[0], best[1], px, py)
    best_actual = cheb(best[0], best[1], ox, oy)
    for nx, ny, dx, dy in my_moves[1:]:
        s = cheb(nx, ny, px, py)
        a = cheb(nx, ny, ox, oy)
        if s < best_score or (s == best_score and a < best_actual):
            best_score = s
            best_actual = a
            best = (nx, ny, dx, dy)
    return [best[2], best[3]]