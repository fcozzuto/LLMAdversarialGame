def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles_list = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    obs = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def blocked(x, y):
        return (x, y) in obs or x < 0 or x >= w or y < 0 or y >= h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    reachable_resources = []
    for rx, ry in resources:
        if not blocked(rx, ry):
            reachable_resources.append((rx, ry))
    if not reachable_resources:
        return [0, 0]

    best_move = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        best_d = None
        best_val = None
        for rx, ry in reachable_resources:
            d = cheb(nx, ny, rx, ry)
            v = (d, -(rx + ry), rx, ry)
            if best_val is None or v < best_val:
                best_val = v
                best_d = d
        opp_d = cheb(nx, ny, ox, oy)
        score = (best_d, opp_d, dx, dy)
        if best_move is None or score < best_move[0]:
            best_move = (score, dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[1], best_move[2]]