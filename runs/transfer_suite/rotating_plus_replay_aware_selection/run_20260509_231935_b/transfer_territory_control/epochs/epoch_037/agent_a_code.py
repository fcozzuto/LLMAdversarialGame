def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    sx, sy = int(sx), int(sy)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Deterministic target choice: prefer nearest unclaimed; else nearest opponent territory; else stay.
    if unclaimed:
        tx, ty = min(unclaimed, key=lambda p: (md(sx, sy, p[0], p[1]), p[0], p[1]))
        mode = 0
    elif opp_terr:
        tx, ty = min(opp_terr, key=lambda p: (md(sx, sy, p[0], p[1]), p[0], p[1]))
        mode = 1
    else:
        return [0, 0]

    # Rotate direction order deterministically by turn_index to reduce loops.
    t = int(observation.get("turn_index", 0))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    r = t % 9
    dirs = dirs[r:] + dirs[:r]

    best_move = (0, 0)
    best_val = -10**18
    dist0 = md(sx, sy, tx, ty)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            val = -10**12
        else:
            n_unclaimed = (nx, ny) in set(unclaimed) if unclaimed else False
            n_opp = (nx, ny) in opp_terr
            n_self = (nx, ny) in self_terr

            d1 = md(nx, ny, tx, ty)
            progress = dist0 - d1
            val = progress * 10

            if n_unclaimed:
                val += 50 if mode == 0 else 20
            if n_opp:
                val += 80 if mode == 1 else 60
            if n_self:
                val -= 3  # slight penalty to avoid wasting moves reclaiming ourselves

            # Extra: if mode is attack, bias toward capturing opponent territory adjacency.
            if mode == 1 and n_opp:
                val += 15

            # Small deterministic tie-breaker favoring straight moves toward target.
            if dx == 0 or dy == 0:
                val += 1

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]