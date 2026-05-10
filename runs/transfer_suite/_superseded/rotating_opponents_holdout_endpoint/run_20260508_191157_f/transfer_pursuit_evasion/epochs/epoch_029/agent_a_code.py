def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("flee" in role) or ("escape" in role)
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def in_bounds(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx > dy else dy
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    # Target corner to bias behavior deterministically
    if is_evader:
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        tx, ty = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    def score_cell(x, y):
        if (x, y) in obs: return -10**9
        d_opp = cheb(x, y)
        d_corner = abs(x - tx) + abs(y - ty)
        # Evader: maximize distance from pursuer and move toward far corner; Pursuer: minimize.
        # Small tie-breakers to avoid obstacles/edges deterministically.
        edge_pen = (x == 0) + (x == w - 1) + (y == 0) + (y == h - 1)
        obs_pen = 0
        if obstacles:
            for px, py in obstacles:
                if abs(x - px) + abs(y - py) == 1: obs_pen = 1
        if is_evader:
            return (d_opp * 1000) + (d_corner * 10) - edge_pen - obs_pen
        else:
            return (-d_opp * 1000) + (-d_corner * 10) - edge_pen - obs_pen

    best_move = (0, 0)
    best_score = -10**18
    # Deterministic iteration order
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny): 
            continue
        sc = score_cell(nx, ny)
        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]