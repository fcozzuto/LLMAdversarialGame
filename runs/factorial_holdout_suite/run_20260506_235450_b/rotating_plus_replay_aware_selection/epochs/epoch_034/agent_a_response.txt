def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal or not resources:
        return [0, 0]

    # 1-step lookahead: pick move that maximizes advantage toward best reachable resource
    best_move = (0, 0, -10**9, 0)
    for dx, dy, nx, ny in legal:
        best_val = -10**18
        best_t = None
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can secure: maximize (do - ds); break ties by smaller ds.
            # Add slight deterministic preference to upper-left to stabilize.
            val = (do - ds) * 1000 - ds
            if val > best_val:
                best_val = val
                best_t = (rx, ry, ds, do)
            elif val == best_val and best_t is not None:
                if ds < best_t[2]:
                    best_t = (rx, ry, ds, do)
                elif ds == best_t[2]:
                    if rx < best_t[0] or (rx == best_t[0] and ry < best_t[1]):
                        best_t = (rx, ry, ds, do)
        # Secondary: also consider overall closeness to resources from nx,ny
        crowd = 10**9
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            ds2 = cheb(nx, ny, rx, ry)
            if ds2 < crowd:
                crowd = ds2
        move_key = (best_val, -crowd, -nx, -ny)
        if move_key > (best_move[2], -best_move[3], -sx, -sy):
            best_move = (dx, dy, best_val, crowd)

    return [int(best_move[0]), int(best_move[1])]