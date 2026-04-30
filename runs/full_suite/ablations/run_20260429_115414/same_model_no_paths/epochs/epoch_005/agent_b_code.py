def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    me = tuple(observation.get("self_position", (0, 0)))
    opp = tuple(observation.get("opponent_position", (0, 0)))
    obstacles = set(tuple(o) for o in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or []) if tuple(r) not in obstacles]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = me[0] + dx, me[1] + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if resources:
        best = None
        for dx, dy in legal:
            nx, ny = me[0] + dx, me[1] + dy
            p = cheb((nx, ny), opp)
            d = None
            for r in resources:
                rd = cheb((nx, ny), r)
                if d is None or rd < d:
                    d = rd
            key = (d, -p)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    tx, ty = w // 2, h // 2
    best = None
    for dx, dy in legal:
        nx, ny = me[0] + dx, me[1] + dy
        key = (cheb((nx, ny), (tx, ty)), cheb((nx, ny), opp))
        if best is None or key < best[0]:
            best = (key, (dx, dy))
    return [best[1][0], best[1][1]]