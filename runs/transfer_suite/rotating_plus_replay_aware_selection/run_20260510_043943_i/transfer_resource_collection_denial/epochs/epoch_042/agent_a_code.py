def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    def free_nbrs(x, y):
        cnt = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                cnt += 1
        return cnt

    res_set = set(tuple(p) for p in resources)
    if not resources:
        # deterministic: head to nearest corner away from opponent x,y
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        bestv = -10**18
        for cx, cy in corners:
            v = (man(ox, oy, cx, cy) - man(sx, sy, cx, cy)) * 10 - man(sx, sy, cx, cy)
            if v > bestv:
                bestv = v
                best = (cx, cy)
        tx, ty = best
        dx = 0
        if tx > sx:
            dx = 1
        elif tx < sx:
            dx = -1
        dy = 0
        if ty > sy:
            dy = 1
        elif ty < sy:
            dy = -1
        return [dx, dy]

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        # if we can land on a resource, prioritize strongly
        land = 1 if (nx, ny) in res_set else 0
        # race evaluation: choose resource where we beat opponent most
        race = -10**18
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # prefer resources we can reach first; also prefer being closer overall
            v = (do - ds) * 120 - ds
            if ds == 0:
                v += 10**8
            if v > race:
                race = v
        # safety: prefer states with more available neighbors, slightly avoid opponent adjacency
        safety = free_nbrs(nx, ny) * 3 - man(nx, ny, ox, oy) // 2
        score = race + safety + land * 10**7
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    # If all candidate moves were blocked, stay (engine keeps in place anyway)
    return [best_move[0], best_move[1]]