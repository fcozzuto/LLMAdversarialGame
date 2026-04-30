def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((p[0], p[1]) for p in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return max(abs(a[0]-b[0]), abs(a[1]-b[1]))  # Chebyshev for diagonal
    def occupied(x, y): return (x, y) in obs_set

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if resources:
        best = None
        for rx, ry in resources:
            if occupied(rx, ry): 
                continue
            d1 = dist((sx, sy), (rx, ry))
            d2 = dist((ox, oy), (rx, ry))
            if d2 < 1e9:
                # Favor resources opponent is unlikely to reach first; also prefer nearer.
                val = d1 - 0.35*d2
            else:
                val = d1
            # Slightly prefer closer to our side to reduce mid-field collisions
            val += 0.02*(rx/(w-1) + ry/(h-1))
            if best is None or val < best[0]:
                best = (val, rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = (w-1)//2, (h-1)//2

    # Opponent avoidance: avoid stepping into squares close to opponent if possible.
    def opp_pen(nx, ny):
        d = dist((nx, ny), (ox, oy))
        return 0 if d >= 2 else (10 if d == 0 else 4 if d == 1 else 2)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if occupied(nx, ny): 
            continue
        score = dist((nx, ny), (tx, ty)) + opp_pen(nx, ny)
        # Also reduce chance of head-on with opponent by discouraging moving closer to them when tied target.
        if score == 0:
            pass
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]