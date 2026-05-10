def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((int(x), int(y)) for x, y in obs_list)

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y): 
        return 0 <= x < gw and 0 <= y < gh

    def valid(x, y): 
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obstacle_adj(x, y):
        c = 0
        for ddx in (-1, 0, 1):
            nx = x + ddx
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ny = y + ddy
                if (nx, ny) in obstacles:
                    c += 1
        return c

    if not resources:
        return [0, 0]

    move_best = [0, 0]
    best = -10**18
    # Deterministic tie-break order
    candidates = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        adj_pen = obstacle_adj(nx, ny) * 0.25

        # If we are on a resource, prefer it strongly.
        on_resource = 0
        if (nx, ny) in set((int(rx), int(ry)) for rx, ry in resources):
            on_resource = 30

        best_cell = -10**18
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer being closer than opponent; also prefer absolute closeness.
            cell = (40 - ds * 3) + (do - ds) * 6 - adj_pen
            if (nx, ny) == (rx, ry):
                cell += 50
            if cell > best_cell:
                best_cell = cell

        score = best_cell + on_resource
        if score > best:
            best = score
            move_best = [dx, dy]

    return move_best