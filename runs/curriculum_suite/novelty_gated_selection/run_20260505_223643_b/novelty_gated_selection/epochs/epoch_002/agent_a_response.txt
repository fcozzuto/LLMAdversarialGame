def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best_total = -10**18
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Choose a resource we can reach not slower than the opponent; otherwise fall back to any resource.
        best_res = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if ds <= do:
                score = 200 - ds  # strongly prefer "contested or winning" resources
                # small bonus for resources that are also far from opponent (harder to steal next)
                score += 0.2 * cheb(rx, ry, ox, oy)
                if score > best_res:
                    best_res = score
        if best_res <= -10**17:
            # Fallback: go toward the closest resource, but avoid moving too close to opponent.
            best_res = max((200 - cheb(nx, ny, rx, ry) for rx, ry in resources))

        # Anti-intercept: keep distance from opponent.
        intercept = cheb(nx, ny, ox, oy)
        total = best_res - 0.15 * intercept

        if total > best_total:
            best_total = total
            best_move = [dx, dy]

    return best_move