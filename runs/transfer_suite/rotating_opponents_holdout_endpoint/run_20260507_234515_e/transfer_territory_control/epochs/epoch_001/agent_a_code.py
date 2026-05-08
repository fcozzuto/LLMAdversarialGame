def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", [])
    obstacles = {(p[0], p[1]) for p in obstacles}
    unclaimed = set(observation.get("unclaimed_cells", []))
    self_terr = set(observation.get("self_territory", []))
    opp_terr = set(observation.get("opponent_territory", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    un_list = list(unclaimed)
    un_list = un_list[:20]

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in unclaimed:
            pr = 4
        elif (nx, ny) in opp_terr:
            pr = 3
        elif (nx, ny) in self_terr:
            pr = 1
        else:
            pr = 0
        d_op = dist(nx, ny, ox, oy)
        d_un = 999
        for px, py in un_list:
            d = dist(nx, ny, px, py)
            if d < d_un:
                d_un = d
        val = pr * 100000 - d_op * 100 - d_un
        if val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]