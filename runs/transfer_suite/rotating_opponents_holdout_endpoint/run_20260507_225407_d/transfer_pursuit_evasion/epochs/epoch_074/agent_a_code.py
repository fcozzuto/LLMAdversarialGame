def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles or not inb(x, y)
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    role = (observation.get("self_role") or "").lower()
    pursuer = ("purs" in role)  # heuristic from role naming

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18 if not pursuer else 10**18

    # Tie-break deterministically toward reducing/expanding cheb, then toward moving off current corner/edge.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny): 
            continue
        d = cheb(nx, ny, ox, oy)
        # Secondary: distance to nearest obstacle cell (approx local safety)
        local_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                xx, yy = nx + ax, ny + ay
                if (xx, yy) in obstacles:
                    local_obs += 1
        edge = (0 if 0 < nx < w - 1 else 1) + (0 if 0 < ny < h - 1 else 1)
        # Deterministic additional preference based on board quadrants
        quad_pref = (1 if (nx < w // 2) == (ny < h // 2) else 0)

        if pursuer:
            score = d * 100 + local_obs * 5 + edge * 2 - quad_pref
            if score < best_score:
                best_score, best_move = score, [dx, dy]
        else:
            score = -d * 100 + local_obs * 5 + edge * 2 - quad_pref
            if score < best_score:
                best_score, best_move = score, [dx, dy]

    # If all moves blocked (unlikely), stay.
    return best_move