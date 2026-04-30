def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def best_target():
        if not resources:
            return (w//2, h//2)
        best = None
        best_pr = None
        min_opp = None
        min_opp_res = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            pr = (od - sd)
            if min_opp is None or od < min_opp:
                min_opp = od
                min_opp_res = (rx, ry)
            if best_pr is None or pr > best_pr:
                best_pr = pr
                best = (rx, ry)
        if best_pr is not None and best_pr >= 0:
            return best
        return min_opp_res if min_opp_res is not None else best

    tx, ty = best_target()

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        dt = cheb(nx, ny, tx, ty)
        do = cheb(nx, ny, ox, oy)
        score = -dt * 10 + do * 0.1
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]