def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    self_role = observation.get("self_role", "")
    ox, oy = opp_pos[0], opp_pos[1]
    sx, sy = self_pos[0], self_pos[1]
    is_pursuer = "pursur" in str(self_role).lower()
    obst = set((p[0], p[1]) for p in obstacles)
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx*dx + dy*dy
    best = None
    if is_pursuer:
        for dx, dy, nx, ny in legal:
            if nx == ox and ny == oy:
                return [dx, dy]
        # minimize distance; tie-break deterministically
        best_key = None
        for dx, dy, nx, ny in legal:
            key = (dist2(nx, ny), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
    else:
        # evade: maximize distance; tie-break deterministically
        best_key = None
        for dx, dy, nx, ny in legal:
            key = (-dist2(nx, ny), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
    return [int(best[0]), int(best[1])]