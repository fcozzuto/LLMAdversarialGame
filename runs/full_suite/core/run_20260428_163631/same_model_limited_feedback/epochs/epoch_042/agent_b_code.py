def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return max(dx, dy)  # Chebyshev for 8-dir

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        # deterministic fallback: move away from opponent if possible, else toward any direction
        best = (0, 0, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = dist((nx, ny), (ox, oy)) - dist((sx, sy), (ox, oy))
            if score > best[2]:
                best = (dx, dy, score)
        return [best[0], best[1]]

    # Pick target that we can reach earlier than opponent; tie-break by deterministic coordinate order
    best_target = None
    best_key = None
    for rx, ry in resources:
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # Main: maximize advantage ds-do (prefer smaller ds, larger difference: use -ds + do)
        # Use key: (adv, -ds, -do, -rx, -ry) with deterministic selection
        key = ((do - ds), (-ds), (-do), (-rx), (-ry))
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    # If opponent is closer by a lot, bias to a different corner resource by swapping tie-break
    if dist((ox, oy), (tx, ty)) + 1 < dist((sx, sy), (tx, ty)):
        # choose resource maximizing do-ds (i.e., where we are relatively closer), else keep current
        for rx, ry in sorted(resources, key=lambda p: (p[0], p[1]), reverse=True):
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            if do - ds >= 1:
                tx, ty = rx, ry
                break

    # Step toward target, avoiding obstacles
    # Tie-break by deterministic move ordering
    move_order = moves[:]  # already deterministic
    best = (0, 0, -10**9)
    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Score balances progress to target, and staying away from opponent if tied
        score = -dist((nx, ny), (tx, ty))
        score += 0.01 * dist((nx, ny), (ox, oy))
        # Prefer moves that don't increase distance to target too much
        score -= 0.001 * max(0, dist((nx, ny), (tx, ty)) - dist((sx, sy), (tx, ty)))
        if score > best[2]:
            best = (dx, dy, score)

    return [best[0], best[1]]