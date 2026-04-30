def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx, cy = w // 2, h // 2
    best = (None, -10**18)

    # If no resources, just move to increase distance from opponent while heading to center
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            val = (cd(nx, ny, ox, oy) - 0.2 * cd(nx, ny, cx, cy))
            if val > best[1]:
                best = ((dx, dy), val)
        return [best[0][0], best[0][1]]

    # New policy: maximize advantage against opponent over a chosen resource, with tie-breakers
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        self_c = cd(nx, ny, cx, cy)
        opp_c = cd(ox, oy, cx, cy)

        best_adv = -10**18
        for rx, ry in resources:
            ds = cd(nx, ny, rx, ry)
            do = cd(ox, oy, rx, ry)
            adv = do - ds  # positive means after this move we're closer than opponent
            # Prefer targets also near where opponent currently is less useful (reduce its ability)
            # Add small penalty if moving away from center while adv is small.
            if adv > best_adv:
                best_adv = adv

        # Primary: winning race advantage; Secondary: closeness to center (to prevent being trapped by obstacles)
        val = best_adv * 10 - self_c + (0.15 * (opp_c - self_c))
        # Tertiary: prefer moves that don't step into dead-end by reducing total distance to all resources
        if val == best[1]:
            total = 0
            for rx, ry in resources:
                total += cd(nx, ny, rx, ry)
            val = val - 0.001 * total

        if val > best[1]:
            best = ((dx, dy), val)

    return [best[0][0], best[0][1]]