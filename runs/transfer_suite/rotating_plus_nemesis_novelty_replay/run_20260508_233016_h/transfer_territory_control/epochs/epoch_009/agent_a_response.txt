def choose_move(observation):
    x, y = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(a, b):
        d = a - b
        return d if d >= 0 else -d

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Find a deterministic "edge" target: nearest unclaimed to our current territory (Manhattan).
    targets = list(unclaimed)
    if targets:
        best_t = targets[0]
        best_d = 10**9
        if self_terr:
            for tx, ty in targets:
                dmin = 10**9
                for sx, sy in self_terr:
                    d = md(tx, sx) + md(ty, sy)
                    if d < dmin:
                        dmin = d
                        if dmin == 0:
                            break
                if dmin < best_d or (dmin == best_d and (ty, tx) < (best_t[1], best_t[0])):
                    best_d, best_t = dmin, (tx, ty)
        else:
            best_t = min(targets, key=lambda p: (md(p[0], x) + md(p[1], y), p[1], p[0]))
    else:
        best_t = None

    # Opponent position for threat: aim to block near their edge by valuing capture squares.
    opp_pos = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = opp_pos[0], opp_pos[1]

    best_key = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue

        # Immediate gain
        if (nx, ny) in opp_terr:
            gain = 4
        elif (nx, ny) in unclaimed:
            gain = 2
        elif (nx, ny) in self_terr:
            gain = 1
        else:
            gain = 0

        # Encourage edge expansion: prefer stepping closer to chosen unclaimed target.
        if best_t is not None:
            tx, ty = best_t
            curd = md(x, tx) + md(y, ty)
            newd = md(nx, tx) + md(ny, ty)
            prog = curd - newd
        else:
            prog = 0

        # Safety: avoid positions that are "tight" against obstacles.
        obs_adj = 0
        for ax, ay in moves:
            tx, ty = nx + ax, ny + ay
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                obs_adj += 1

        # Edge pressure against opponent: slightly favor moves closer to their position if it also captures.
        opp_dist = md(nx, ox) + md(ny, oy)

        # Deterministic tie-breakers
        key = (
            gain * 100 + prog * 3 - obs_adj * 2,
            -opp_dist,
            -abs(nx - (w - 1)) - abs(ny - (h - 1)),
            dy,
            dx,
        )
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move