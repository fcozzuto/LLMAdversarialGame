def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in self_role) or (self_role == "pursuer")

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_dxdy = (0, 0)
    if is_pursuer:
        best_score = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles:
                continue
            dist = cheb(nx, ny, ox, oy)
            # Primary: minimize distance (maximize -dist). Tie-break: prefer closer to center to reduce escape.
            score = -dist * 100 - (abs(nx - cx) + abs(ny - cy))
            if dist == 0:
                score = 10**9  # immediate capture
            if score > best_score:
                best_score = score
                best_dxdy = (dx, dy)
    else:
        best_score = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            dist = cheb(nx, ny, ox, oy)
            # Primary: maximize distance. Secondary: prefer moving away from opponent and to a safer corner.
            opp_dx = nx - ox
            opp_dy = ny - oy
            if opp_dx < 0: opp_dx = -opp_dx
            if opp_dy < 0: opp_dy = -opp_dy
            corner_bias = (abs(nx - (0 if ox > w/2 else w-1)) + abs(ny - (0 if oy > h/2 else h-1)))
            score = dist * 100 + (opp_dx + opp_dy) * 10 + corner_bias
            # discourage getting stuck near center if opponent is close
            if dist <= 1:
                score -= (abs(nx - cx) + abs(ny - cy)) * 5
            if score > best_score:
                best_score = score
                best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]