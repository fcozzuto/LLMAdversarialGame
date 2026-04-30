def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles_list = observation.get("obstacles", []) or []
    resources_list = observation.get("resources", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list)
    resources = [(int(p[0]), int(p[1])) for p in resources_list]
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    def collide(x, y):
        return (x, y) in obstacles or (x, y) == (ox, oy)
    def dist(a, b):
        ax, ay = a; bx, by = b
        return max(abs(ax - bx), abs(ay - by))
    valid = lambda x, y: inside(x, y) and not collide(x, y)
    best = [0, 0]
    # Simple heuristic: move towards nearest resource if safe; else stay or approach opponent cautiously.
    if resources:
        best_res = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = None
            for rx, ry in resources:
                if not inside(rx, ry) or (rx, ry) in obstacles:
                    continue
                d = dist((nx, ny), (rx, ry))
                if score is None or d < score:
                    score = d
            if score is None:
                score = 999
            # Prefer smaller distance to resource; tie-breaker: keep away from opponent
            opp_dist = dist((nx, ny), (ox, oy))
            s = (score, -opp_dist)
            if best_score is None or s > best_score:
                best_score = s
                best = [dx, dy]
    else:
        # No resources visible: advance towards center while avoiding obstacle and opponent
        cx, cy = (w // 2, h // 2)
        best_local = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            toward = dist((nx, ny), (cx, cy))
            away_opp = dist((nx, ny), (ox, oy))
            s = (toward, away_opp)
            if best_score is None or s > best_score:
                best_score = s
                best_local = [dx, dy]
        if best_local is not None:
            best = best_local
    return best