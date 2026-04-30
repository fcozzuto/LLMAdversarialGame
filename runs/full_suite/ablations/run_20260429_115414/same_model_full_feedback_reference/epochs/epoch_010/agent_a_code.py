def choose_move(observation):
    W = observation["grid_width"]; H = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    res = []
    for p in resources:
        if p and len(p) >= 2:
            t = (p[0], p[1])
            if t not in obs:
                res.append(t)

    def inb(x, y): return 0 <= x < W and 0 <= y < H
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    def legal(x, y): return inb(x, y) and (x, y) not in obs

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    if res:
        # Immediate pickup
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny) and (nx, ny) in res:
                return [dx, dy]

        best_score = None
        best_move = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue

            my_d = cheb(nx, ny, ox, oy)
            # Prefer moving toward resources that opponent can't reach no later than us
            min_good = 10**9
            min_any = 10**9
            for rx, ry in res:
                md = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                if md < min_any: min_any = md
                if md < od and md < min_good: min_good = md

            if min_good < 10**9:
                score = (100 - min_good) + (my_d * 0.1)
            else:
                score = (100 - min_any) + (my_d * 0.05)  # just avoid opponent a bit

            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
        return best_move

    # No resources: move to maximize distance from opponent
    best_d = -1
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        if d > best_d:
            best_d = d
            best_move = [dx, dy]
    return best_move