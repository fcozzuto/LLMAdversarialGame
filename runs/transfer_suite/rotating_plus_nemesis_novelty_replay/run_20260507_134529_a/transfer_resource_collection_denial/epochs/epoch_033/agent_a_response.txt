def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            # Score by best contest advantage against opponent for any remaining resource
            # Higher is better; add small tie-break for moving toward closer resources.
            val = -10**18
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                advantage = do - ds  # positive means we are closer in fewer steps
                # Encourage not just stealing but also progressing quickly once contested
                local = advantage * 1000 - ds
                if local > val:
                    val = local
            # Prefer staying moves only if they don't hurt advantage
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: head to a safe central point deterministically
    tx, ty = w // 2, h // 2
    best = (0, 0)
    bestd = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
        d = cheb(nx, ny, tx, ty)
        if d < bestd:
            bestd = d
            best = (dx, dy)
    return [int(best[0]), int(best[1])]