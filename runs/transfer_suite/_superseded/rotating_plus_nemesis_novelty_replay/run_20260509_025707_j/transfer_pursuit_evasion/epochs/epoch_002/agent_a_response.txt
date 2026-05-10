def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    self_role = observation.get("self_role", "") or ""
    is_pursuer = ("pursuer" in self_role.lower()) or ("pursuit" in self_role.lower())

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            moves.append((dx, dy))
    # deterministic tie-break order: prefer non-staying less often but fixed
    moves.sort(key=lambda t: (t[0] == 0 and t[1] == 0, abs(t[0]) + abs(t[1]), t[0], t[1]))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # simple reachability: count free neighbors to avoid getting cornered
    def free_degree(x, y):
        c = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                nx, ny = x + ddx, y + ddy
                if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                    c += 1
        return c

    # Evader corner targets with obstacle-aware bias: maximize distance and local mobility
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if not is_pursuer:
        # pick best corner among those with at least some mobility from our current vicinity
        # (deterministic: fixed order + score)
        best_corner = corners[0]
        best_corner_score = None
        for cx, cy in corners:
            s = dist2(sx, sy, cx, cy) + 3 * free_degree(cx, cy)
            if best_corner_score is None or s > best_corner_score:
                best_corner_score = s
                best_corner = (cx, cy)
        tx, ty = best_corner
    else:
        tx, ty = ox, oy

    # Greedy evaluation with obstacle friction and pursuer-wall-running counterplay
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        if is_pursuer:
            # Prefer moves that reduce distance; also avoid positions with low mobility (get stuck behind walls)
            score = -dist2(nx, ny, tx, ty) + 0.4 * free_degree(nx, ny)
            # Minor bias to move in the direction of opponent with diagonal preference
            score += -0.05 * (abs(nx - ox) + abs(ny - oy))
        else:
            # Evade: maximize distance; prefer moves that increase mobility and avoid being forced toward opponent
            score = dist2(nx, ny, ox, oy) + 1.2 * free_degree(nx, ny)
            # Also bias toward the chosen corner while not sacrificing separation
            score += 0.02 * dist2(nx, ny, tx, ty)
            # Repel from obstacle-adjacent "tight" tiles
            near_obs = 0
            for ddx in (-1, 0, 1):
                for ddy in (-1, 0, 1):
                    if ddx == 0 and ddy == 0:
                        continue
                    ax, ay = nx + ddx, ny + ddy
                    if in_bounds(ax, ay) and (ax, ay) in obstacles:
                        near_obs += 1
            score -= 0.25 * near_obs
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]