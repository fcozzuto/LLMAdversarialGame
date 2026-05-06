def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # keep away while drifting toward center
        tx = w // 2 - 1 if ox > w // 2 - 1 else w // 2
        ty = h // 2 - 1 if oy > h // 2 - 1 else h // 2
        best = None
        bestv = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = (cheb(nx, ny, ox, oy), -cheb(nx, ny, tx, ty))
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose move that maximizes lead on the most "contested" reachable resource.
    best = legal[0]
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # local evaluation: consider top few resources by our closeness
        candidates = []
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive means we are closer than opponent
            candidates.append((ds, -lead, lead, rx, ry))
        candidates.sort()
        for ds, _, lead, rx, ry in candidates[:6]:
            # Prefer securing a resource that we can beat the opponent on, otherwise maximize lead.
            # Also slightly reward moving toward the resource.
            v = (lead, -ds, -cheb(nx, ny, rx, ry), -abs(nx - rx) - abs(ny - ry))
            if best_score is None or v > best_score:
                best_score = v
                best = (dx, dy)

    return [best[0], best[1]]