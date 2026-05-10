def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_unclaimed_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                c += 1
        return c

    def corner_bias(x, y):
        # Prefer staying off the inner side of our home-corner line to reduce flips/contests.
        # home corner is whichever corner we started from; infer from current distance parity.
        if sx <= w - 1 - sx:
            home_x = 0
        else:
            home_x = w - 1
        if sy <= h - 1 - sy:
            home_y = 0
        else:
            home_y = h - 1
        dist_home = abs(x - home_x) + abs(y - home_y)
        dist_op = abs(x - (w - 1 - home_x)) + abs(y - (h - 1 - home_y))
        return (dist_op - dist_home)  # higher is better

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        v = 0
        if (nx, ny) in opp_terr:
            v += 5
        if (nx, ny) in unclaimed:
            v += 7
        if (nx, ny) in self_terr:
            v += 1

        v += 2 * adj_unclaimed_count(nx, ny)

        # Encourage progressing to the opponent side (territory contest tends to happen there).
        v += 0.1 * corner_bias(nx, ny)

        # Avoid getting stuck on a cell that gives few prospects.
        v -= 0.01 * (abs(nx - sx) + abs(ny - sy) == 0)

        # Deterministic tie-break: closer to opponent, then lexicographically smaller move delta.
        opp_target_x = w - 1 - (0 if sx <= w - 1 - sx else w - 1)
        opp_target_y = h - 1 - (0 if sy <= h - 1 - sy else h - 1)
        prox = abs(nx - opp_target_x) + abs(ny - opp_target_y)

        key = (v, -prox, -dx, -dy)
        if best is None or key > best:
            best = key
            best_score = v
            best_move = [dx, dy]

    # If all moves invalid (shouldn't), stay.
    return best_move if best is not None else [0, 0]