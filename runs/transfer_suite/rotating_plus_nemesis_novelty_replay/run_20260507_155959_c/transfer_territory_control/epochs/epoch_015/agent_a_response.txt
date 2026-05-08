def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = (observation.get("self_position", [0, 0]) + [0, 0])[:2]
    ox, oy = (observation.get("opponent_position", [w - 1, h - 1]) + [w - 1, h - 1])[:2]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    self_cells = set(tuple(xy) for xy in (observation.get("self_territory", []) or []))
    opp_cells = set(tuple(xy) for xy in (observation.get("opponent_territory", []) or []))
    unclaimed = set(tuple(xy) for xy in (observation.get("unclaimed_cells", []) or []))

    # Opponent "center" estimate
    if opp_cells:
        xs = [x for x, _ in opp_cells]
        ys = [y for _, y in opp_cells]
        opp_center = (sum(xs) // len(xs), sum(ys) // len(ys))
    else:
        opp_center = (ox, oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_score = -10**9

    def cell_score(x, y):
        if (x, y) in obstacles or not inb(x, y):
            return -10**8
        base = 0
        if (x, y) in self_cells:
            base = 0
        elif (x, y) in opp_cells:
            base = 3  # flipping enemy territory on entry is good
        elif (x, y) in unclaimed:
            base = 5  # fastest growth target
        else:
            base = 1  # empty/unknown still ok if useful

        # Strategic bias: take space away from opponent center but also contest if close.
        d_opp = abs(x - opp_center[0]) + abs(y - opp_center[1])
        d_ours = abs(x - 0) + abs(y - 0)  # bias toward our corner
        # Encourage moving to corners/border while avoiding being trapped in center
        corner_bonus = (min(x, w - 1 - x) + min(y, h - 1 - y))
        # Lower corner_bonus means closer to border/corner
        border_pref = -corner_bonus * 0.15

        # If unclaimed are near, prefer the nearest-ish direction
        nearest_unclaimed = None
        for ux, uy in unclaimed:
            if abs(ux - x) + abs(uy - y) <= 2:
                nearest_unclaimed = 0
                break
        local_unclaimed = 1 if nearest_unclaimed is not None else 0

        return base * 10 + d_opp * 0.25 + d_ours * 0.05 + border_pref + local_unclaimed

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sc = cell_score(nx, ny)
        # Mild preference for reducing distance to opponent when we can flip
        if (nx, ny) in opp_cells:
            sc += -(abs(nx - ox) + abs(ny - oy)) * 0.05
        if sc > best_score:
            best_score = sc
            best = [dx, dy]

    return [int(best[0]), int(best[1])]