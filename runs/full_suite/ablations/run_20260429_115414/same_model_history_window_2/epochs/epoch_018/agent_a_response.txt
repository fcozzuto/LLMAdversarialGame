def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    remaining = observation.get("remaining_resource_count", len(resources))

    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources or remaining <= 0:
        tx, ty = (ox, oy)  # deterministic: go toward opponent corner for endgame stability
        best = None; bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # Ensure deterministic targeting: evaluate "best contested resource" for each candidate move
    best = None; bestv = -10**18
    for dx, dy, nx, ny in legal:
        v = 0.0
        if (nx, ny) in blocked:
            v -= 1e9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            take = 5.0 if (ds == 0) else 0.0
            # Prefer resources we can reach earlier than opponent; break ties by absolute proximity
            score = (do - ds) + 0.08 * (do + ds) * (-1) + take
            # small incentive to progress along our move
            score += -0.01 * cheb(nx, ny, rx, ry)
            if score > v:
                v = score
        # tie-break against staying put only slightly (deterministic order already helps)
        if dx == 0 and dy == 0:
            v -= 0.02
        if v > bestv:
            bestv = v; best = (dx, dy)

    return [int(best[0]), int(best[1])]