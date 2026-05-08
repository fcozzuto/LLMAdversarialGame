def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    is_evader = ("evader" in self_role) or ("pursuer" in opponent_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        tx, ty = corner
    else:
        corner = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        tx, ty = corner

    def king_dist(x, y):
        dx = x - ox
        if dx < 0:
            dx = -dx
        dy = y - oy
        if dy < 0:
            dy = -dy
        return dx + dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best = None
    best_dxdy = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = king_dist(nx, ny)

        # Obstacle proximity penalty to avoid getting trapped near walls.
        prox = 0
        for ax in (nx - 1, nx, nx + 1):
            for ay in (ny - 1, ny, ny + 1):
                if (ax, ay) in obs:
                    prox += 1

        # Edge bias for wall-run evasion / pursuit tightening.
        edge_bias = 0
        if nx == 0 or nx == w - 1:
            edge_bias += 2
        if ny == 0 or ny == h - 1:
            edge_bias += 2

        # Deterministic directional pull toward/away from a corner.
        corner_pull = (abs(nx - tx) + abs(ny - ty)) - (abs(sx - tx) + abs(sy - ty))
        # If evader: increase distance from opponent and move toward chosen corner; pursuer: opposite.
        score = d
        if is_evader:
            score = score + 0.5 * (-corner_pull) + 0.15 * edge_bias - 0.3 * prox
            better = (best is None) or (score > best) or (score == best and (dx, dy) < tuple(best_dxdy))
        else:
            score = -d + 0.5 * (corner_pull) + 0.15 * edge_bias - 0.3 * prox
            better = (best is None) or (score > best) or (score == best and (dx, dy) < tuple(best_dxdy))

        if better:
            best = score
            best_dxdy = [dx, dy]

    return [int(best_dxdy[0]), int(best_dxdy[1])]