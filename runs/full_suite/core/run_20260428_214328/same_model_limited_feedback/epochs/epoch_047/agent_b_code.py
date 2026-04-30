def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []); obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    candidates = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    deltas = candidates
    if not resources:
        # fall back: move to keep centralization while avoiding obstacles
        tx, ty = w//2, h//2
        best = (-10**9, (0,0))
        for dx, dy in deltas:
            nx, ny = sx+dx, sy+dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            d = abs(nx-tx) + abs(ny-ty)
            if -d > best[0]:
                best = (-d, (dx, dy))
        return best[1]
    # Deterministically target the resource where we have the strongest immediate advantage
    # (opponent farther than us), then move toward it while contesting.
    def dist(a, b):
        ax, ay = a; bx, by = b
        return abs(ax-bx) + abs(ay-by)
    best_target = resources[0]
    best_adv = -10**9
    for rx, ry in resources:
        adv = dist((ox, oy), (rx, ry)) - dist((sx, sy), (rx, ry))
        # tie-break: nearer to us
        if adv > best_adv or (adv == best_adv and dist((sx, sy), (rx, ry)) < dist((sx, sy), best_target)):
            best_adv = adv
            best_target = (rx, ry)
    tx, ty = best_target
    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx+dx, sy+dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        myd = dist((nx, ny), (tx, ty))
        oppd = dist((ox, oy), (tx, ty))
        # Prefer moves that reduce our distance to target, and increase the advantage margin.
        score = (oppd - myd) * 100 - myd
        # Small secondary: avoid giving opponent a closer path to any resource than we have.
        worst_gap = 10**9
        for rx, ry in resources:
            gap = dist((ox, oy), (rx, ry)) - dist((nx, ny), (rx, ry))
            if gap < worst_gap:
                worst_gap = gap
        score += worst_gap * 2
        # Mild repulsion from opponent to reduce chance of losing contested pickups (if close).
        score -= dist((nx, ny), (ox, oy)) * 0.2
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]