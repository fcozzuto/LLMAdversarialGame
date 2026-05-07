def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 if d1 > d2 else d2

    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [int(dx), int(dy)]

    # pick target: prefer resources where we're not behind the opponent
    best = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        our_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        lead = our_d - opp_d  # <= 0 means we are closer or tied
        key = (1 if lead > 0 else 0, lead, our_d, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # choose move that best improves our advantage over that target
    cur_our_d = cheb(sx, sy, tx, ty)
    cur_opp_d = cheb(ox, oy, tx, ty)

    chosen = [0, 0]
    chosen_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
            dx, dy = 0, 0
        our_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        advantage = opp_d - our_d  # higher is better
        step = max(abs(dx), abs(dy))
        # primary: maximize advantage; secondary: reduce distance to target; tertiary: deterministic tie-break
        key = (-advantage, our_d, step, nx, ny)
        if chosen_key is None or key < chosen_key:
            chosen_key = key
            chosen = [int(dx), int(dy)]

    # If standing still is best but we are not on target, nudge deterministically toward it
    if chosen == [0, 0] and cur_our_d != 0:
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            return [int(dx), int(dy)]
    return chosen