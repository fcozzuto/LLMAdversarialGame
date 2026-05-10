def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or (("evad" not in self_role) and ("evad" in opp_role) is False)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
    far_corner = max(corners, key=lambda c: abs(c[0]-ox) + abs(c[1]-oy))
    def dist2(x1, y1, x2, y2):
        dx, dy = x1-x2, y1-y2
        return dx*dx + dy*dy

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_opp = dist2(nx, ny, ox, oy)
        d_corner = dist2(nx, ny, far_corner[0], far_corner[1])
        d_obs_min = 0
        if obstacles:
            d_obs_min = min((nx-bx)*(nx-bx) + (ny-by)*(ny-by) for (bx, by) in obstacles)
        # Pursuer: minimize distance, stay away from obstacles.
        # Evader: maximize distance; bias toward far corner; avoid obstacles.
        if is_pursuer:
            score = -d_opp + 0.002 * d_obs_min - 0.0001 * d_corner
        else:
            score = d_opp + 0.0015 * d_corner + 0.002 * d_obs_min
        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return best_move