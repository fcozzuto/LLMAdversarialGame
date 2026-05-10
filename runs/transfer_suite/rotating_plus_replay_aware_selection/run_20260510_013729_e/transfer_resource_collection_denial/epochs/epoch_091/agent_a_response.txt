def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]
    obst = {(x, y) for x, y in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obst

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def pick_target(px, py):
        # tie-break: closer first, then lexicographically smaller
        best = None
        bestd = 10**9
        for rx, ry in resources:
            d = dist(px, py, rx, ry)
            if d < bestd or (d == bestd and (rx, ry) < best):
                bestd = d
                best = (rx, ry)
        return best[0], best[1], bestd

    tx0, ty0, d0 = pick_target(sx, sy)
    # If we can capture immediately, do it.
    if d0 == 0:
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18

    # Opponent's greedy target assumption from their current position
    otx, oty, od = pick_target(ox, oy)

    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not legal(nx, ny):
            continue
        ntx, nty, ourd = pick_target(nx, ny)
        # Value: beat opponent by reducing our distance to the shared "contested" resource.
        # If we pick a different resource, reward still by minimizing ourd and increasing opponent distance to ours.
        contested = (ntx, nty) == (otx, oty)
        opp_to_ours = dist(ox, oy, ntx, nty)
        opp_to_their = od
        # Encourage moving closer to the resource we think is best, and additionally discourage opponent's access.
        val = (opp_to_ours - ourd) * (2 if contested else 1) + (opp_to_their - od) * 0
        # Secondary tie-break: prefer moves that get us closer to our immediate target.
        if val > best_val or (val == best_val and ourd < dist(sx, sy, tx0, ty0)):
            best_val = val
            best_move = (mdx, mdy)

    mdx, mdy = best_move
    return [int(mdx), int(mdy)]