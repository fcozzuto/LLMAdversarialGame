def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal_from(x, y):
        out = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                out.append((dx, dy, nx, ny))
        return out

    legal = legal_from(sx, sy)
    if not legal:
        return [0, 0]

    # No resources: drift to center while avoiding obstacles and opponent
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in legal:
            d = cheb(nx, ny, tx, ty)
            prox = 0
            for ax, ay in obstacles:
                t = cheb(nx, ny, ax, ay)
                if t <= 2:
                    prox += (3 - t)
            op_dist = cheb(nx, ny, ox, oy)
            key = (d, -op_dist, prox, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1]

    best_move = None
    best_score = None

    for dx, dy, nx, ny in legal:
        # Obstacle proximity penalty
        prox = 0
        for ax, ay in obstacles:
            t = cheb(nx, ny, ax, ay)
            if t <= 2:
                prox += (3 - t)

        # Choose resource that maximizes "reach advantage" vs opponent
        move_adv = -10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            adv = oppd - myd  # positive means we can reach sooner (or at least tie-break better)
            # favor landing on resource immediately
            if myd == 0:
                cand = 10**6 - prox
            else:
                cand = adv * 20 - myd * 2 - prox
            if cand > move_adv:
                move_adv = cand

        # If we can't find a good advantage, increase distance from opponent to force different contest
        op_dist = cheb(nx, ny, ox, oy)
        if move_adv < 0:
            move_adv += op_dist * 3

        if best_score is None or move_adv > best_score or (move_adv == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = move_adv
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]