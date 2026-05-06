def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Choose a target: prefer cells where opponent is closer than we are, then closer overall,
    # and prefer earlier (lower-x,y) deterministically as tie-break.
    best = None
    best_key = None
    for cx, cy in resources:
        sd = cheb(sx, sy, cx, cy)
        od = cheb(ox, oy, cx, cy)
        key = (od - sd, -sd, -cx, -cy)
        if best_key is None or key > best_key:
            best_key = key
            best = (cx, cy)
    tx, ty = best

    # If we're already closer to the target than opponent, add slight goal to maintain advantage.
    advantage = 1 if cheb(sx, sy, tx, ty) < cheb(ox, oy, tx, ty) else 0

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obs:
                continue
            nd = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            self_gain = (cheb(sx, sy, tx, ty) - nd)
            # Deny: if the move reduces opponent's distance to us (interception proxy)
            deny = -cheb(ox, oy, nx, ny)
            # If opponent is closer to our target, emphasize moves that reduce their lead.
            lead = (od - nd)
            key = (lead, self_gain, deny, -abs(nx - tx) - abs(ny - ty), -nx, -ny)
            # Deterministic slight adjustment based on advantage
            if advantage:
                key = (key[0] + 0.01, key[1], key[2], key[3], key[4], key[5])
            moves.append((key, (dx, dy)))

    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: t[0], reverse=True)
    return [moves[0][1][0], moves[0][1][1]]