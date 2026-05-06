def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    best_move = None
    best_key = None
    # If no resources, just move to maximize distance from opponent (avoid giving them easy access).
    if not resources:
        for dx, dy, nx, ny in moves:
            d = cheb(nx, ny, ox, oy)
            key = (d, -abs(nx - ox) - abs(ny - oy), dx, dy)
            if best_key is None or key > best_key:
                best_key = key
                best_move = [dx, dy]
        return best_move if best_move is not None else [0, 0]

    # Evaluate each move by best attainable resource with a deterministic greedy look.
    # Key prefers: (opp_my_diff advantage), then closeness to resource, then avoiding being behind.
    for dx, dy, nx, ny in moves:
        local_best = None
        local_key = None
        for cx, cy in resources:
            my_d = cheb(nx, ny, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            # higher is better: want opp slower than us, and be close to the resource
            adv = opp_d - my_d
            # Tie-breaks: be closer, and prefer cells that also don't reduce advantage too much
            key = (adv, -my_d, -cheb(nx, ny, ox, oy), cx, cy)
            if local_key is None or key > local_key:
                local_key = key
                local_best = (cx, cy, my_d, opp_d, adv)
        # Also add a small penalty if move would directly allow opponent to be strictly closer to *some* resource
        # next step (shadow predator archetype tends to capitalize).
        shadow_pen = 0
        # compute opponent advantage margin across resources; if opponent is already ahead everywhere, stick with max local_key anyway
        for cx, cy in resources:
            opp_my_d = cheb(ox, oy, cx, cy)
            my_d0 = cheb(nx, ny, cx, cy)
            if opp_my_d < my_d0:
                shadow_pen += (my_d0 - opp_my_d)
        key_move = (local_key[0], local_key[1], -local_key[2], -shadow_pen, dx, dy)
        if best_key is None or key_move > best_key:
            best_key = key_move
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]