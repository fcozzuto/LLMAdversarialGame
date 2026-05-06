def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = abs(nx - tx) + abs(ny - ty)
            if d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]] if best[1] or best[2] else [0, 0]

    # Pick a resource by "advantage": (opponent farther than us).
    best_res = None
    best_adv = -10**18
    for rx, ry in resources:
        ourd = abs(rx - sx) + abs(ry - sy)
        oppd = abs(rx - ox) + abs(ry - oy)
        adv = oppd - ourd
        if adv > best_adv:
            best_adv = adv
            best_res = (rx, ry)
    if best_res is None:
        return [0, 0]
    tx, ty = best_res

    # Evaluate next moves: improve our distance to target + preserve advantage + avoid close opponent.
    best = (10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ourd = abs(tx - nx) + abs(ty - ny)
        oppd = abs(tx - ox) + abs(ty - oy)

        # Recompute advantage after move, but only for the chosen target (keeps strategy stable).
        adv_after = oppd - ourd

        # Anti-collision / shadowing: if opponent is very close, prioritize widening distance.
        dist_to_opp_next = abs(nx - ox) + abs(ny - oy)
        opp_term = 0
        if dist_to_opp_next <= 2:
            opp_term = -8 * dist_to_opp_next  # larger dist is better (lower score)

        # Small bias to avoid wall-hugging oscillations: prefer moves that reduce ourd first.
        wall_bias = 0
        if nx in (0, w - 1) or ny in (0, h - 1):
            wall_bias = 1

        score = ourd * 5 - adv_after * 3 + wall_bias + opp_term
        tie = (abs(dx) + abs(dy))  # slight preference for staying (deterministic tie-break)
        key = (score, tie, dx, dy)
        if key < (best[0], best[0]*0 + 0, best[1], best[2]):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]