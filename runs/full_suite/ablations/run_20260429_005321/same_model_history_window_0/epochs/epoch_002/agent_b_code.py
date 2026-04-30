def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d(a, b, c, e):
        dx = a - c
        dy = b - e
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    bestv = -10**9
    opp_adj = {(ox+i, oy+j) for i in (-1,0,1) for j in (-1,0,1)}

    # If no resources, just drift away from opponent.
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # Prefer moving to maximize distance.
            val = d(nx, ny, ox, oy)
            # Small preference for not stepping adjacent.
            if (nx, ny) in opp_adj:
                val -= 2
            if val > bestv:
                bestv = val
                best = [dx, dy]
        if best is None:
            return [0, 0]
        return best

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Evaluate by choosing the best resource to contest after this move.
        best_resource_score = -10**9
        for rx, ry in resources:
            ds = d(nx, ny, rx, ry)
            do = d(ox, oy, rx, ry)
            # Positive means we are closer than opponent.
            contest = (do - ds)
            val = contest * 3 - ds
            if (nx, ny) == (rx, ry):
                val += 1000
            if val > best_resource_score:
                best_resource_score = val
        # Discourage stepping into/near opponent.
        danger = 0
        if (nx, ny) in opp_adj:
            danger = 6
        # Mild obstacle/edge pressure to reduce getting stuck: penalize proximity to obstacles.
        local_pen = 0
        for ax, ay in ((nx-1, ny),(nx+1, ny),(nx, ny-1),(nx, ny+1)):
            if (ax, ay) in obstacles:
                local_pen += 1
        v = best_resource_score - danger - local_pen
        if v > bestv:
            bestv = v
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best