def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) == 2:
            obst.add((int(p[0]), int(p[1])))
    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) == 2:
            t = (int(p[0]), int(p[1]))
            if t not in obst:
                resources.append(t)
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # If no resources, head for a corner away from opponent by Chebyshev "push".
    if not resources:
        tx = 0 if ox > sx else w - 1
        ty = 0 if oy > sy else h - 1
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = -cheb(nx, ny, tx, ty) - 0.15 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Score each move by the best guaranteed advantage over opponent to any resource.
    # Prefer taking/contesting resources quickly; tie-break with safety and slight corner pressure.
    corner = (w - 1, h - 1) if (ox + oy) < (w - 1 - sx + h - 1 - sy) else (0, 0)
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy, nx, ny in legal:
        best_adv = -10**18
        best_tie = 10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Encourage moves that reduce our distance or increase their distance.
            adv = (do - ds) * 10 - ds
            # Prefer resources we can reach at the same time or sooner.
            if ds <= do:
                adv += 5
            if adv > best_adv or (adv == best_adv and ds < best_tie):
                best_adv = adv
                best_tie = ds
        # Safety: lightly penalize moves that get closer to opponent's current focus corner.
        safety = -0.25 * cheb(nx, ny, ox, oy)
        corner_push = -0.03 * cheb(nx, ny, corner[0], corner[1])
        val = best_adv + safety + corner_push
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]