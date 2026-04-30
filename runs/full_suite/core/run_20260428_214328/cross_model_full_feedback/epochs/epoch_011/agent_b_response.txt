def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    resources = [(p[0], p[1]) for p in (observation.get("resources", []) or [])]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    # 8-neighborhood
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    # blocked check
    def blocked(nx, ny):
        return not inside(nx, ny) or (nx, ny) in obstacles or (nx, ny) == (ox, oy)

    # If there are resources, prioritize getting closer to ones not too near opponent
    if resources:
        best = None
        best_score = None
        res_set = set(tuple(r) for r in resources)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny): continue
            # distance to closest resource from new pos
            cand = None
            for rx, ry in resources:
                d = max(abs(rx - nx), abs(ry - ny))  # Chebyshev distance
                if cand is None or d < cand:
                    cand = d
            if cand is None: cand = 0
            # distance to opponent
            opp_dist = max(abs(ox - nx), abs(oy - ny))
            # score: closer to resource (smaller cand) and farther from opponent (larger opp_dist)
            score = (-cand) + opp_dist
            if best_score is None or score > best_score:
                best_score = score
                best = [dx, dy]
        if best is not None:
            return best
        return [0, 0]

    # No resources left; simple approach: move to maximize distance from opponent while staying within grid and not colliding
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny): continue
        dist_opp = max(abs(ox - nx), abs(oy - ny))
        dist_me = max(abs(nx - sx), abs(ny - sy))
        score = dist_opp - dist_me
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]
    return best if best is not None else [0, 0]