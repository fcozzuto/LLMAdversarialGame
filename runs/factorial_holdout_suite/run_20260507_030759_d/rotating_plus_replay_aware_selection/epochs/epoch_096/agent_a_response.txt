def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    if (sx, sy) in resources:
        return [0, 0]
    if w <= 0 or h <= 0:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        dy = by - ay
        axd = dx if dx >= 0 else -dx
        ayd = dy if dy >= 0 else -dy
        return axd if axd > ayd else ayd

    best_move = (0, 0)
    best_key = (-10**18, 10**18, 0)

    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue

        # Advantage over opponent for each resource from the candidate next position.
        # Prefer states where we can beat opponent by the largest margin.
        best_adv = -10**18
        best_self_dist = 10**18
        best_opp_dist = 10**18

        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            sd = cheb(nsx, nsy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if adv > best_adv or (adv == best_adv and (sd < best_self_dist or (sd == best_self_dist and od < best_opp_dist))):
                best_adv = adv
                best_self_dist = sd
                best_opp_dist = od

        # Tie-break: maximize future security (larger opp-self distance), then closer to best resource, then keep position if equally good.
        key = (best_adv, -best_self_dist, 1 if (mdx == 0 and mdy == 0) else 0)
        # Convert to ascending for comparisons by using consistent tuple direction
        key2 = (key[0], -key[1], -key[2])  # (adv desc via compare inverted later)
        # We'll compare manually:
        if (best_key[0] < key2[0]) or (best_key[0] == key2[0] and (best_key[1] > key2[1] or (best_key[1] == key2[1] and best_key[2] > key2[2]))):
            best_key = key2
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]