def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_for_cell(cx, cy):
        if not resources: return 0
        bestv = -10**18
        for rx, ry in resources:
            sd = cheb(cx, cy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where we're closer than opponent; tie-break by closeness and remaining resources density proxy.
            v = (od - sd) * 1000 - sd
            if v > bestv: bestv = v
        return bestv

    # If already on a resource, stay (collects) unless blocked logic suggests otherwise.
    for rx, ry in resources:
        if sx == rx and sy == ry:
            return [0, 0]

    best_move = (0, 0)
    best_val = -10**18
    # Move to a high-value target; among equally valued moves, prefer smaller cheb distance to the best target next.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
        v = best_for_cell(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]