def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role) or ("escape" in role)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_score = None

    # Precompute obstacle proximity (deterministic, local)
    obs_list = [(int(o[0]), int(o[1])) for o in (observation.get("obstacles", []) or []) if isinstance(o, (list, tuple)) and len(o) >= 2]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        dist = cheb(nx, ny, ox, oy)

        # Obstacle avoidance: discourage moving adjacent to obstacles and into "tight" cells
        adj = 0
        tight = 0
        for oxp, oyp in obs_list:
            d = cheb(nx, ny, oxp, oyp)
            if d == 0:
                adj += 10
            elif d == 1:
                adj += 3
            elif d == 2:
                adj += 1
        # tightness: count legal neighbors (prefer higher if evader, lower if pursuer)
        neigh_legal = 0
        for mdx, mdy in moves:
            tx, ty = nx + mdx, ny + mdy
            if legal(tx, ty):
                neigh_legal += 1
        tight = neigh_legal

        # Center bias
        center_dist = abs(nx - cx) + abs(ny - cy)

        if is_evader:
            score = dist * 1000 + tight * 5 - adj * 50 - int(center_dist * 2)
        else:
            score = (-dist) * 1000 + (8 - tight) * 5 - adj * 50 - int(center_dist * 1)

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]