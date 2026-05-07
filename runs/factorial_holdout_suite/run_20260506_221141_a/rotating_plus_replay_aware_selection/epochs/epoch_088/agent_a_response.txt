def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    def legal(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Drift if no visible resources: go to our far corner while keeping away from opponent
    if not resources:
        tx = gw - 1 if sx < gw // 2 else 0
        ty = gh - 1 if sy < gh // 2 else 0
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            v = -cheb(nx, ny, tx, ty) + 0.25 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_move, best_val = [0, 0], -10**18
    oppd0 = cheb(sx, sy, ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Pick the resource that maximizes our advantage in earliest arrival; also prefer nearer targets
        v = 0
        for rx, ry in resources:
            mydist = cheb(nx, ny, rx, ry)
            oppdist = cheb(ox, oy, rx, ry)
            # If we can arrive earlier, value strongly; if not, still allow pursuit but penalize
            adv = oppdist - mydist
            target_v = 12 * adv - 0.8 * mydist
            # Small extra: prefer resources that are closer to us than to opponent already at current turn
            target_v += 0.15 * (oppd0 - cheb(nx, ny, ox, oy))
            if target_v > v:
                v = target_v

        # Tie-break: keep moving so we don't stall; but still allow [0,0] if best
        if dx == 0 and dy == 0:
            v -= 0.05
        if v > best_val:
            best_val = v
            best_move = [dx, dy]

    return best_move