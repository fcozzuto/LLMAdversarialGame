def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def clamp_move(nx, ny):
        if nx < 0: nx = 0
        if nx >= w: nx = w - 1
        if ny < 0: ny = 0
        if ny >= h: ny = h - 1
        if (nx, ny) in obstacles:
            return sx, sy
        return nx, ny

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    my_half_right = (sx <= w // 2)
    opp_half_right = (ox <= w // 2)

    best_move = (0, 0)
    best_val = -10**18

    # Deterministic tie-break: prefer smaller dx, then smaller dy.
    for dxm, dym in moves:
        nx, ny = clamp_move(sx + dxm, sy + dym)
        myd = (nx, ny)

        # Heuristic: compete for the closest few resources, using (opp_dist - my_dist)
        # to prefer resources we reach earlier than the opponent.
        cand = []
        for rx, ry in resources:
            md = dist(myd, (rx, ry))
            od = dist((ox, oy), (rx, ry))
            # extra pressure if we are on "front" relative to opponent
            front_bonus = 0
            if my_half_right and not opp_half_right and rx > (w // 2 - 1):
                front_bonus = 1
            elif (not my_half_right) and opp_half_right and rx < (w // 2):
                front_bonus = 1
            cand.append((od - md + front_bonus, md, od, rx, ry))

        cand.sort(key=lambda t: (-t[0], t[1], t[2], t[3], t[4]))
        topk = cand[:3]

        val = 0
        for gain, md, od, rx, ry in topk:
            if (rx, ry) == (nx, ny):
                val += 1000 - md
            # Encourage both reaching quickly and surpassing opponent.
            val += gain * 25 - md * 2 + (0 if od == 0 else 1)

        # Mild directional preference toward nearest resource overall to avoid dithering.
        nearest = min(resources, key=lambda r: dist(myd, r))
        val += 2 / (1 + dist(myd, nearest))

        if val > best_val or (val == best_val and (dxm, dym) < best_move):
            best_val = val
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]