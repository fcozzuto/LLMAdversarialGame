def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def pos_of(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", v.get("location", None)))
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return int(p[0]), int(p[1])
        return None

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        p = pos_of(o)
        if p:
            x, y = p
            if in_bounds(x, y):
                obstacles.add((x, y))

    s = pos_of(observation.get("self_position", None))
    o = pos_of(observation.get("opponent_position", None))
    if not s:
        s = (0, 0)
    if not o:
        o = s

    resources = []
    for r in observation.get("resources", []) or []:
        p = pos_of(r)
        if p:
            x, y = p
            if in_bounds(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    sx, sy = s
    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best_move = (0, 0)
    best_val = -10**18

    if not resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    def mindist(px, py):
        md = 10**9
        for rx, ry in resources:
            d = abs(px - rx) + abs(py - ry)
            if d < md:
                md = d
        return md

    opp_best = mindist(o[0], o[1])

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        my_best = mindist(nx, ny)
        value = (opp_best - my_best) * 100 - my_best
        if nx == o[0] and ny == o[1]:
            value += 10**6
        if value > best_val:
            best_val = value
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]