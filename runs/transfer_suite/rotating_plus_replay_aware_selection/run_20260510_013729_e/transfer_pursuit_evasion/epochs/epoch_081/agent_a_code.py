def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_ev = ("evad" in self_role) or ("run" in self_role) or ("escap" in self_role)
    opp_ev = ("evad" in opp_role) or ("run" in opp_role) or ("escap" in opp_role)
    pursuer = (not self_ev) or opp_ev

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        dist = cheb(nx, ny, ox, oy)
        # Small deterministic tie-break favoring stability toward center for evasion, toward blocker-free advance for pursuit
        center_bias = -(abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
        # Obstacle proximity penalty
        near_obs = 0
        for ax, ay in ((nx-1, ny),(nx+1, ny),(nx, ny-1),(nx, ny+1),(nx-1, ny-1),(nx+1, ny-1),(nx-1, ny+1),(nx+1, ny+1)):
            if (ax, ay) in obstacles:
                near_obs += 1

        if pursuer:
            val = (-dist) * 100 - near_obs * 5 + center_bias * 0.01
        else:
            val = (dist) * 100 - near_obs * 5 + center_bias * 0.01

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]