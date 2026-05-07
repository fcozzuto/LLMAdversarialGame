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
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal or not resources:
        return [0, 0]

    # Deterministic tie-break keys prefer: bigger advantage, then smaller self distance, then smaller distance to any resource.
    best_key = None
    best_move = None
    for dx, dy, nx, ny in legal:
        best_adv = None
        best_sd = None
        best_md = None
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive means self closer
            if best_adv is None or adv > best_adv or (adv == best_adv and (sd < best_sd or (sd == best_sd and sd < best_md))):
                best_adv, best_sd, best_md = adv, sd, sd
        # If any resource is closer for us (adv>0), prioritize strongest advantage; else minimize opponent edge and approach closest resource.
        # Use additional scoring to avoid oscillation: prefer decreasing distance to the chosen resource compared to current position.
        # Estimate current distance for same best_adv resource by scanning again lightly (still deterministic).
        curr_best_sd = None
        if best_adv is not None:
            for rx, ry in resources:
                rx, ry = int(rx), int(ry)
                sd0 = cheb(sx, sy, rx, ry)
                od0 = cheb(ox, oy, rx, ry)
                if od0 - sd0 == best_adv:
                    if curr_best_sd is None or sd0 < curr_best_sd:
                        curr_best_sd = sd0
            if curr_best_sd is None:
                curr_best_sd = 10**9
        # Advantage primary, then smaller self distance after move, then improvement over current, then lexicographic stable by move order.
        improve = curr_best_sd - best_sd if curr_best_sd != 10**9 else 0
        key = (best_adv, -best_sd, improve, -abs(nx - ox) - abs(ny - oy), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]