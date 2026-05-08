def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obs_list = observation.get("obstacles", [])
    obs = {(p[0], p[1]) for p in obs_list} if obs_list else set()
    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("pursuer" in self_role) or ("pursuer" in opp_role) or (not ("evader" in self_role))
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs
    def cheb(x, y):
        dx = x - ox; dy = y - oy
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        d = cheb(nx, ny)
        score = d if is_pursuer else -d
        if best_score is None:
            best_score = score; best = [dx, dy]
        else:
            if is_pursuer:
                if score < best_score:
                    best_score = score; best = [dx, dy]
                elif score == best_score and (dx, dy) == (0, 0):
                    best = [dx, dy]
            else:
                if score > best_score:
                    best_score = score; best = [dx, dy]
                elif score == best_score and (dx, dy) == (0, 0):
                    best = [dx, dy]
    if best is None:
        return [0, 0]
    return best