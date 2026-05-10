def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs = set(tuple(p) for p in (observation.get("obstacles") or []))
    un_t = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]
    un_set = set(un_t)
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    options = [(-1, -1), (-1, 0), (-1, 1),
               (0, -1), (0, 0), (0, 1),
               (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def mindist_to_list(x, y, lst):
        best = 10**9
        for a, b in lst:
            d = abs(a - x) + abs(b - y)
            if d < best:
                best = d
        return best if lst else best

    def cell_value(nx, ny):
        if (nx, ny) in un_set:
            return 5.0
        if (nx, ny) in opp_t:
            return 2.2  # flipping on entry
        return 0.7

    # Choose move maximizing immediate cell value + progress toward unclaimed
    # Tie-break deterministically by preferring moves with smaller dx,dy lexicographically.
    best = None
    best_score = -10**18
    for dx, dy in options:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        score = cell_value(nx, ny)
        d_un = mindist_to_list(nx, ny, un_t)
        score += 0.35 * (-d_un if d_un < 10**8 else -0)
        # Also drift slightly toward opponent so we contest frontier (opponent center-claim style)
        score += 0.08 * (-(abs(nx - ox) + abs(ny - oy)))
        # Prefer staying still only if scores equal
        score += -0.01 * (abs(dx) + abs(dy))
        key = (score, -abs(dx) - abs(dy), -nx, -ny, dx, dy)
        if best is None or key > best:
            best = key
            best_score = score

    if best is None:
        return [0, 0]
    # Extract the winning move from the last part of key
    return [int(best[4]), int(best[5])]