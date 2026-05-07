def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    res_set = set()
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def nearest_dist(px, py):
        best = 10**9
        for rx, ry in resources:
            d = cheb(px, py, rx, ry)
            if d < best:
                best = d
        return best

    moves = [(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    best_move = (0, 0)
    best_val = -10**18
    # Strongly commit toward a nearby target if it yields advantage; otherwise pressure the nearest resource race.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my_d = nearest_dist(nx, ny)
        opp_d = nearest_dist(ox, oy)
        pickup_bonus = 6 if (nx, ny) in res_set else 0

        # If adjacent to a resource for us while opponent is not, prioritize.
        adj_bonus = 3 if my_d == 1 else 0
        opp_adj_pen = -2 if opp_d == 1 else 0

        # Also lightly favor moves that reduce our distance more than opponent's distance.
        cur_my_d = nearest_dist(sx, sy)
        delta = (cur_my_d - my_d)

        val = pickup_bonus + adj_bonus + opp_adj_pen + (my_d - opp_d) * -10 + delta * 2
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]