def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb2(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def step_toward(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
        return None

    scored = []
    for rx, ry in resources:
        sd = cheb2(sx, sy, rx, ry)
        od = cheb2(ox, oy, rx, ry)
        # Prefer resources we're closer to; if we are not, still deny by chasing where opponent is relatively weaker.
        scored.append((od - sd, -sd, rx, ry))
    scored.sort(reverse=True)

    for _, _, rx, ry in scored:
        mv = step_toward(rx, ry)
        if mv is not None:
            return mv

    # Fallback: move to a non-obstacle neighbor that maximizes (opponent-self distance gain) locally
    best = [0, 0]
    bestv = -10**9
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            # Greedy local: compare to closest resource in that neighbor
            local = None
            md = 10**9
            for rx, ry in resources:
                d = cheb2(nx, ny, rx, ry)
                if d < md:
                    md = d
                    local = (rx, ry)
            if local is None:
                continue
            rx, ry = local
            v = cheb2(ox, oy, rx, ry) - md
            if v > bestv:
                bestv = v
                best = [dx, dy]
    return best if best is not None else [0, 0]