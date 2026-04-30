def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = observation.get("obstacles") or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles}

    resources = observation.get("resources") or []
    res = [(int(p[0]), int(p[1])) for p in resources]
    on_res = set(res)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # If no resources, just keep distance from opponent while staying safe.
    if not res:
        best_move = (0, 0)
        best_sc = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            sc = cheb(nx, ny, ox, oy)
            if sc > best_sc:
                best_sc = sc
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    best_move = (0, 0)
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_self_near = 10**9
        min_gap = 10**9
        for rx, ry in res:
            ds = cheb(nx, ny, rx, ry)
            if ds < d_self_near:
                d_self_near = ds
            do = cheb(ox, oy, rx, ry)
            gap = ds - do  # negative means we are closer than opponent to this resource
            if gap < min_gap:
                min_gap = gap

        sc = 0
        if (nx, ny) in on_res:
            sc += 2000
            sc += 50 - d_self_near
        sc += -d_self_near * 5
        sc += -min_gap * 12

        # Mildly prefer moving away from opponent when not directly taking a resource.
        if (nx, ny) not in on_res:
            cur_gap = cheb(sx, sy, ox, oy)
            nxt_gap = cheb(nx, ny, ox, oy)
            sc += (nxt_gap - cur_gap) * 2

        if sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]