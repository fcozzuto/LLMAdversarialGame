def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = [0, 0]
        best_score = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                score = -(cheb(nx, ny, ox, oy))
                if score > best_score:
                    best_score = score
                    best = [dx, dy]
        return best

    best = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        # pick target resource where we are relatively closer than opponent
        target_score = -10**18
        target_dist = 10**9
        for rx, ry in resources:
            d1 = cheb(nx, ny, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            rel = d2 - d1  # >0 means we are closer than opponent
            # prefer capturing soon, and winning relative race
            cand = 50 * rel - d1
            if rx == nx and ry == ny:
                cand += 1000
            if cand > target_score or (cand == target_score and d1 < target_dist):
                target_score = cand
                target_dist = d1
        # additional pressure: avoid moving toward opponent if that helps their race
        opp_pressure = cheb(nx, ny, ox, oy)
        score = target_score - 2 * opp_pressure
        if score > best_score:
            best_score = score
            best = [dx, dy]
    return best