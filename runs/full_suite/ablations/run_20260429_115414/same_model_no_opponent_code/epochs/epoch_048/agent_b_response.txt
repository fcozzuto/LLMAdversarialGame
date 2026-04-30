def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = resources[0]
        bestv = -10**9
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer being much closer; slight preference for nearer absolute distance
            v = (do - ds) * 10 - ds
            if v > bestv:
                bestv = v
                best = (rx, ry)
        tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_d = cheb(sx, sy, tx, ty)
    bestm = (0, 0)
    bestscore = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ns_d = cheb(nx, ny, tx, ty)
        # If we are moving away too much, penalize heavily
        progress = cur_d - ns_d

        # Opponent pressure: prefer moves that increase opponent distance to target and reduce ours-to-them distance
        no_d = cheb(ox, oy, tx, ty)
        opp_gain = (no_d - no_d)  # stable baseline
        # Actually compute opponent potential next-to-target distance (opponent stays unknown, approximate by current)
        # Add penalty if opponent is very close to us
        adj_pen = 0
        ddx = ox - nx
        if ddx < 0: ddx = -ddx
        ddy = oy - ny
        if ddy < 0: ddy = -ddy
        if ddx <= 1 and ddy <= 1:
            adj_pen = 8

        score = progress * 30 - ns_d - adj_pen + opp_gain
        # If target is already on our next tile, strongly prefer it
        if nx == tx and ny == ty:
            score += 10**6
        if score > bestscore:
            bestscore = score
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]