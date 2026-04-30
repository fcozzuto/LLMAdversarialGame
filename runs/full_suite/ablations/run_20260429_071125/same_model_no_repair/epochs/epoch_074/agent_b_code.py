def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        # go to farther corner from opponent, but prefer staying on the same diagonal direction
        corners = [(0, 0), (w - 1, h - 1), (0, h - 1), (w - 1, 0)]
        best_move = (0, 0, sx, sy)
        bestv = -10**18
        # deterministic preference order already in legal list
        for dx, dy, nx, ny in legal:
            # choose which corner aligns with move (prefer corner maximizing cheb to opponent)
            v = 0
            for cx, cy in corners:
                v2 = cheb(nx, ny, cx, cy) - 0.9 * cheb(nx, ny, ox, oy) + 0.05 * cheb(sx, sy, cx, cy)
                if v2 > v:
                    v = v2
            if v > bestv:
                bestv = v
                best_move = (dx, dy, nx, ny)
        return [best_move[0], best_move[1]]

    best = None
    bestv = -10**18

    # greedy: pick move that maximizes "capture pressure" over each resource
    # capture pressure: I want resources closer than opponent; if tie, closer to me; else still go for nearer.
    for dx, dy, nx, ny in legal:
        v = 0
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # positive when we can get it earlier; strong bias to immediate adjacency
            gain = (do - ds)
            if ds == 0:
                gain += 5
            v += gain - 0.05 * ds
        # small preference to keep moving generally toward opponent-avoiding direction:
        # discourage moving closer to opponent unless it helps capture pressure
        v -= 0.02 * cheb(nx, ny, ox, oy)
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]