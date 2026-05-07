def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        bestm = [0, 0]
        bestk = None
        for mx, my in cand:
            nx, ny = sx + mx, sy + my
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            k = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty) + ((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)) * 0.0005
            if bestk is None or k < bestk:
                bestk = k
                bestm = [mx, my]
        return bestm

    best_move = [0, 0]
    best_val = None

    for mx, my in cand:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Score the best resource we could plausibly race for from (nx, ny)
        local_best = None
        for rx, ry in resources:
            sd = abs(rx - nx) + abs(ry - ny)
            od = abs(rx - ox) + abs(ry - oy)

            # Main race objective: maximize opp_d - self_d (prefer resources we can reach first)
            race = od - sd

            # Anti-denial: penalize resources that are very close to opponent while we are not
            deny = 0
            if od <= sd:
                deny = (sd - od) * 2.0 + 0.5 * (sd)

            # Sweep-row opponent mitigation: if they likely travel along rows, prefer changing row faster
            row_adv = abs(ry - ny) - abs(ry - sy)  # how much this move changes our row approach
            # Small tie-break to drift toward center
            center = (rx - (w - 1) / 2) * (rx - (w - 1) / 2) + (ry - (h - 1) / 2) * (ry - (h - 1) / 2)

            val = race - deny - 0.02 * row_adv - 0.001 * center - 0.01 * sd
            if local_best is None or val > local_best:
                local_best = val

        if best_val is None or local_best > best_val:
            best_val = local_best
            best_move = [mx, my]

    return best_move if best_move is not None else [0, 0]