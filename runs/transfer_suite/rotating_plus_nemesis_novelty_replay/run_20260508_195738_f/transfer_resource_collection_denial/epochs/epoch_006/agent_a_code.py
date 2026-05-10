def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_resource_value(px, py):
        if not resources:
            # no resources: prefer staying closer to farthest corner from opponent
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            bestv = None
            for cx, cy in corners:
                v = cheb(ox, oy, cx, cy) - cheb(px, py, cx, cy)
                if bestv is None or v > bestv:
                    bestv = v
            return bestv if bestv is not None else 0
        best = -10**9
        for rx, ry in resources:
            myd = cheb(px, py, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            # aim to be strictly earlier; discourage very long trips
            v = (oppd - myd) * 1000 - myd
            if v > best:
                best = v
        return best

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_score = -10**18
    base_val = best_resource_value(sx, sy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            # engine keeps us in place; treat same as (0,0)
            nx, ny = sx, sy
            dx, dy = 0, 0
        v = best_resource_value(nx, ny)
        # prefer improvements; slightly prefer moving (non-stay) if equal
        move_pref = 0 if (dx == 0 and dy == 0) else 1
        score = (v - base_val) * 10000 + v + move_pref
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]