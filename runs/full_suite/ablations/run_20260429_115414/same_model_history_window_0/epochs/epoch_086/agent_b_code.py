def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    best_u = None
    best_move = (0, 0)
    # If no resources, just head toward opponent to contest space
    if not resources:
        tx, ty = ox, oy
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            u = -cheb(nx, ny, tx, ty)
            if best_u is None or u > best_u:
                best_u = u
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Evaluate best resource by advantage: opponent distance minus self distance
        best_adv = None
        best_sd = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if best_adv is None or adv > best_adv or (adv == best_adv and sd < best_sd):
                best_adv = adv
                best_sd = sd
        # Prefer moves that create advantage and also keep you close to a target
        u = best_adv * 100 - best_sd
        if best_u is None or u > best_u:
            best_u = u
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]