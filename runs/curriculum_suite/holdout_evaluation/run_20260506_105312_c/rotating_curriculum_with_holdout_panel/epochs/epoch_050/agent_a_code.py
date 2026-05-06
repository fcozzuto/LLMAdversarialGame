def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = -10**18

    if not resources:
        # Simple deterministic "retreat toward center" when no resources
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
                continue
            # Prefer moves that reduce distance to center, but also keep away from opponent
            val = cheb(cx, cy, ox, oy) - cheb(cx, cy, nx, ny)
            if best is None or val > best_val:
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    opp_near = 10**9
    opp_far = -1
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if d < opp_near:
            opp_near = d
        if d > opp_far:
            opp_far = d

    # "Interceptor": move to maximize opponent's nearest-resource distance while keeping own access decent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        my_near = 10**9
        my_far = -1
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < my_near:
                my_near = d
            if d > my_far:
                my_far = d

        # Encourage reducing my_near, but also "mess with" opponent by chasing distant resources (edge patrol tries edges).
        # Value balances: higher if my_near is small, and if opponent is relatively disadvantaged.
        val = (opp_near - my_near) + (my_far * 0.15) - (abs((nx - ox)) + abs((ny - oy))) * 0.02
        # Slightly prefer moves that increase distance from opponent when opponent is closer to most resources.
        if opp_near <= (opp_far * 0.6):
            val += cheb(nx, ny, ox, oy) * 0.05

        if best is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]] if best else [0, 0]