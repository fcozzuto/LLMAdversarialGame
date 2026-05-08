def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # legal one-step candidates (greedy next move to desired direction)
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    # if current tile has resource, take it
    for r in resources:
        if r[0] == sx and r[1] == sy:
            return [0, 0]

    if not resources:
        # move toward the midpoint (deterministic fallback)
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = min(candidates, key=lambda t: cheb(t[2], t[3], tx, ty))
        return [best[0], best[1]]

    # Choose a resource where we are ahead; else choose one to contest (we are behind least)
    scored = []
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        margin = do - ds  # positive means we arrive earlier
        # tie-break deterministically: prefer nearer, then lexicographic
        scored.append((margin, ds + do, rx, ry))
    scored.sort(key=lambda t: (-t[0], t[1], t[2], t[3]))

    best_margin = scored[0][0]
    # If we can take something first, target best-ahead resource; otherwise contest a closest-behind resource
    target = scored[0] if best_margin > 0 else scored[min(3, len(scored) - 1)]

    rx, ry = target[2], target[3]

    # If we are behind, bias toward moves that reduce the opponent's lead on that target
    # (move maximizing (opponent_dist_after - self_dist_after))
    best = None
    best_val = None
    for dx, dy, nx, ny in candidates:
        self_d = cheb(nx, ny, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)  # opponent position unchanged this turn
        val = (opp_d - self_d, -self_d, abs(nx - ox) + abs(ny - oy), nx, ny)
        if best is None or val > best_val:
            best_val = val
            best = (dx, dy)
    return [best[0], best[1]]