def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs = set((x, y) for x, y in observation.get("obstacles", []))

    role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    pursuer = ("pursuer" in role) or ("evader" in opp_role)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [
        (0, 0), (1, 0), (0, 1), (-1, 0), (0, -1),
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    ]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if pursuer:
        target = min(corners, key=lambda c: (cheb(c[0], c[1], ox, oy), c[0], c[1]))
        best_key = None
        best_move = (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            k = (cheb(nx, ny, ox, oy), cheb(nx, ny, target[0], target[1]), abs(nx - ox) + abs(ny - oy), dx, dy)
            if best_key is None or k < best_key:
                best_key = k
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # evader
    target = max(corners, key=lambda c: (cheb(c[0], c[1], ox, oy), -c[0], -c[1]))
    best_key = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        k = (-cheb(nx, ny, ox, oy), -cheb(nx, ny, target[0], target[1]), abs(nx - ox) + abs(ny - oy), -dx, -dy)
        if best_key is None or k < best_key:
            best_key = k
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]