def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = set(obstacles_raw if isinstance(obstacles_raw, (set, list)) else [])
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    def valid(x, y): return inside(x, y) and (x, y) not in obstacles

    if resources and any(sx == rx and sy == ry for rx, ry in resources):
        return [0, 0]

    candidates = []
    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_self = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            d_opp = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
            score = (-(d_self - d_opp), -d_self, d_opp, dx, dy)
            candidates.append((score, dx, dy))
        if not candidates:
            return [0, 0]
        candidates.sort(reverse=True)
        return [candidates[0][1], candidates[0][2]]
    else:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            score = (d, -cheb(nx, ny, sx, sy), dx, dy)
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]] if best is not None else [0, 0]