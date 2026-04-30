def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    moves = [(dx, dy) for dx, dy in dirs if inb(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]
    if resources:
        tr = None
        best = 10**9
        for rx, ry in resources:
            d = abs(rx - sx) + abs(ry - sy)
            if d < best or (d == best and (rx, ry) < tr):
                best = d
                tr = (rx, ry)
        tx, ty = tr
        def score_move(dx, dy):
            nx, ny = sx + dx, sy + dy
            md = abs(tx - nx) + abs(ty - ny)
            od = abs(ox - nx) + abs(oy - ny)
            return (md, -od)
        bestm = None
        bestv = None
        for dx, dy in moves:
            v = score_move(dx, dy)
            if bestv is None or v < bestv:
                bestv = v
                bestm = (dx, dy)
        return [int(bestm[0]), int(bestm[1])]
    dist_o = abs(ox - sx) + abs(oy - sy)
    def move_score(dx, dy):
        nx, ny = sx + dx, sy + dy
        d = abs(ox - nx) + abs(oy - ny)
        centerx, centery = (w - 1) // 2, (h - 1) // 2
        dc = abs(centerx - nx) + abs(centery - ny)
        return ((d if dist_o <= 2 else -d), dc)
    bestm = None
    bestv = None
    for dx, dy in moves:
        v = move_score(dx, dy)
        if bestv is None or v < bestv:
            bestv = v
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]