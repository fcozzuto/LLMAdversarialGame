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

    def dist2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx*dx + dy*dy

    def move_score(nx, ny):
        if (nx, ny) in obst:
            return -10**18
        for ax in (nx-1, nx, nx+1):
            for ay in (ny-1, ny, ny+1):
                if (ax, ay) in obst:
                    return -10**12

        if resources:
            k = 0.55
            best = -10**18
            # Choose the resource that we can reach relatively earlier than opponent
            for rx, ry in resources:
                if (rx, ry) in obst:
                    continue
                myd = dist2(nx, ny, rx, ry)
                opd = dist2(ox, oy, rx, ry)
                # Primary: minimize myd; Secondary: maximize opd; Tertiary: slight preference for closer to me
                s = (-myd) + k*(opd) - 0.01*myd
                # If at the resource, be decisive
                if myd == 0:
                    s += 10**9
                if s > best:
                    best = s
            # Keep from letting opponent catch us too easily
            best -= 0.12*dist2(nx, ny, ox, oy)
            return best
        else:
            # No resources visible: head to center while keeping away from opponent/obstacles
            cx, cy = (w - 1) // 2, (h - 1) // 2
            return -dist2(nx, ny, cx, cy) - 0.2*dist2(nx, ny, ox, oy)

    best_move = (0, 0)
    best = -10**18
    # Deterministic tie-break order already in moves list
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inside(nx, ny):
            continue
        s = move_score(nx, ny)
        if s > best:
            best = s
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]