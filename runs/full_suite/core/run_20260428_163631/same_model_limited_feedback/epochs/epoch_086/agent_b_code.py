def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def clamp(nx, ny):
        if nx < 0: nx = 0
        if ny < 0: ny = 0
        if nx >= w: nx = w - 1
        if ny >= h: ny = h - 1
        return nx, ny
    if resources:
        tx, ty = resources[0]
        bestd = (tx - x) * (tx - x) + (ty - y) * (ty - y)
        for rx, ry in resources[1:]:
            d = (rx - x) * (rx - x) + (ry - y) * (ry - y)
            if d < bestd:
                bestd = d
                tx, ty = rx, ry
    else:
        tx, ty = 0, 0
    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = clamp(x + dx, y + dy)
        if (nx, ny) in obstacles:
            nx, ny = x, y
            dx, dy = 0, 0
        d_self = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        d_opp = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
        landed_on_resource = 1 if resources and any((nx == rx and ny == ry) for rx, ry in resources) else 0
        score = (landed_on_resource, -d_self, d_opp, -abs(tx - nx) - abs(ty - ny), -abs(ox - nx) - abs(oy - ny))
        if best is None or score > best:
            best = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]