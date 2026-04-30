def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources_list = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    resources = set((p[0], p[1]) for p in resources_list)
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    # All 8 neighbors + stay
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(nx, ny):
        return not inside(nx, ny) or (nx, ny) in obstacles or (nx, ny) == (ox, oy)

    # If there are resources, prefer moving toward closest resource while keeping distance from opponent
    if resources:
        best_move = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny): 
                continue
            # distance to nearest resource from (nx,ny)
            cand = None
            for rx, ry in resources:
                if not inside(rx, ry) or (rx, ry) in obstacles:
                    continue
                d = max(abs(rx - nx), abs(ry - ny))
                if cand is None or d < cand:
                    cand = d
            if cand is None:
                cand = 0
            # distance to opponent
            opp_dist = max(abs(ox - nx), abs(oy - ny))
            # score: smaller resource distance, larger opponent distance
            score = (-cand) + (opp_dist * 0.1)
            if (best_score is None) or (score > best_score):
                best_score = score
                best_move = [dx, dy]
        if best_move is not None:
            return best_move

    # No available resource approach or no resources; go defensively approach center-ish while avoiding opponent
    # Target to move away from opponent when possible, else stay
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        # prefer farther from opponent
        dist = max(abs(ox - nx), abs(oy - ny))
        if (best_score is None) or (dist > best_score):
            best_score = dist
            best_move = [dx, dy]
    if best_move is not None:
        return best_move

    # Fallback
    return [0, 0]