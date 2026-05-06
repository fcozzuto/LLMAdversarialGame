def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Choose target where we beat opponent's distance, and break ties toward opponent-side control.
    best = None
    best_key = (-10**9, -10**9, 10**9)
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer resources we can reach no later than opponent; if so, prioritize larger advantage.
        # Also slightly prefer targets nearer center to reduce corner-guard traps.
        center_bias = 3 - abs(tx - (w - 1) / 2) - abs(ty - (h - 1) / 2)
        reach = do - ds
        if ds == 0:
            key = (10**9, center_bias, 0)
        else:
            # Negative ds penalizes "too far" but only through the main advantage.
            key = (reach, center_bias, ds)
        if key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best

    # If opponent is extremely close and we are not clearly winning the chosen target, step away.
    dso = cheb(sx, sy, ox, oy)
    ds_to_target = cheb(sx, sy, tx, ty)
    if dso <= 2 and (best_key[0] < 0) and ds_to_target > 0:
        best_move = [0, 0]
        best_score = -10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    score = cheb(nx, ny, ox, oy) - cheb(nx, ny, tx, ty)
                    if score > best_score:
                        best_score = score
                        best_move = [dx, dy]
        return best_move

    # Otherwise, move one step that best reduces Chebyshev distance to target, avoiding obstacles.
    best_move = [0, 0]
    best_score = -10**9
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                dist = cheb(nx, ny, tx, ty)
                # Prefer equal-distance moves that increase our separation from opponent.
                score = -dist * 10 + (cheb(nx, ny, ox, oy))
                if score > best_score:
                    best_score = score
                    best_move = [dx, dy]
    return best_move