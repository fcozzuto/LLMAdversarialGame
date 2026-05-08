def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = str(observation.get("self_role", "")).lower()
    is_evader = any(k in role for k in ("evader", "evade", "runner", "flee", "evasion"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    phase = int(observation.get("turn_index", 0)) & 3

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def obst_penalty(x, y):
        # Avoid cells adjacent to obstacles; stronger if very close.
        p = 0
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d == 0:
                return 10**6
            if d == 1:
                p += 7
            elif d == 2:
                p += 2
        return p

    # Simple deterministic target selection
    if is_evader:
        # Run toward a corner that maximizes distance from opponent.
        target = corners[phase]
        best = -10**9
        for c in corners:
            s = cheb(c[0], c[1], ox, oy)
            if s > best:
                best = s
                target = c
        tx, ty = target
    else:
        # Pursue by moving to reduce distance to opponent; tie-break toward opponent corner-pressure.
        tx, ty = ox, oy

    best_move = (0, 0)
    best_score = -10**18 if is_evader else 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        dist_opp = cheb(nx, ny, ox, oy)
        dist_tar = cheb(nx, ny, tx, ty)
        pen = obst_penalty(nx, ny)

        # If evader: maximize distance from opponent and also prefer moving toward target corner.
        if is_evader:
            corner_bias = -dist_tar  # closer to target corner is better (since higher score overall prefers -dist_tar)
            score = (dist_opp * 100) + corner_bias - pen
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        else:
            # Pursuer: minimize distance to opponent; slight bias toward target (opponent cell).
            score = (dist_opp * 100) + dist_tar - pen
            if score < best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]