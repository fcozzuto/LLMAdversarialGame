def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(p[0], p[1]) for p in obstacles}

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx*dx + dy*dy

    def free_neighbors(nx, ny):
        c = 0
        for dxm, dym in moves:
            tx, ty = nx + dxm, ny + dym
            if inside(tx, ty) and (tx, ty) not in obst:
                c += 1
        return c

    def near_obstacle(nx, ny):
        for dxm, dym in moves:
            tx, ty = nx + dxm, ny + dym
            if inside(tx, ty) and (tx, ty) in obst:
                return 1
        return 0

    # If no resources, just survive and drift away from obstacles/opponent pressure
    if not resources:
        best = -10**18
        best_move = [0, 0]
        for dxm, dym in moves:
            nx, ny = x + dxm, y + dym
            if not inside(nx, ny) or (nx, ny) in obst:
                continue
            s = free_neighbors(nx, ny) - 0.05*dist2(nx, ny, ox, oy) - 0.5*near_obstacle(nx, ny)
            if s > best:
                best = s
                best_move = [dxm, dym]
        return best_move

    best = -10**18
    best_move = [0, 0]
    for dxm, dym in moves:
        nx, ny = x + dxm, y + dym
        if not inside(nx, ny) or (nx, ny) in obst:
            continue

        # Choose the target that gives the biggest distance advantage over opponent
        best_adv = -10**18
        for rx, ry in resources:
            if (rx, ry) in obst:
                continue
            myd = dist2(nx, ny, rx, ry)
            opd = dist2(ox, oy, rx, ry)
            adv = opd - myd  # positive if we are closer
            if myd == 0:
                adv += 10**6
            # small tie-break: prefer targets closer to us as long as advantage is similar
            score = adv - 0.01*myd + 0.0005*opd
            if score > best_adv:
                best_adv = score

        # Move quality: keep mobility, avoid getting adjacent to obstacles, and don't waste steps when advantage is small
        mobility = free_neighbors(nx, ny)
        waste = dist2(nx, ny, ox, oy) * 0.0001  # slight deterrent from clustering with opponent
        obs_pen = near_obstacle(nx, ny) * 0.7
        s = best_adv + 0.12*mobility - obs_pen - waste
        if s > best:
            best = s
            best_move = [dxm, dym]
    return best_move