def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if inb(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]
    if not resources:
        # drift toward opponent's side to keep pressure
        tx = (w - 1 if ox <= sx else 0)
        ty = (h - 1 if oy <= sy else 0)
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            d = abs(tx - nx) + abs(ty - ny)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # Advantage: how much closer we are than the opponent to some resource
        # (maximizing opp_dist - my_dist prioritizes contested resources we can reach sooner)
        max_adv = None
        best_my_d_for_adv = None
        for rx, ry in resources:
            my_d = abs(rx - nx) + abs(ry - ny)
            opp_d = abs(rx - ox) + abs(ry - oy)
            adv = opp_d - my_d
            if (max_adv is None or adv > max_adv or (adv == max_adv and my_d < best_my_d_for_adv)):
                max_adv = adv
                best_my_d_for_adv = my_d

        # Secondary objective: if equal advantage, take nearest resource for guaranteed progress
        # Tertiary: avoid moves that let opponent land closer immediately (minimal opp next-distance)
        if max_adv is None:
            continue
        # approximate opponent-next effect without knowing their move: prefer states where our distance is small
        my_nearest = best_my_d_for_adv

        # final tie-break: smaller my_nearest, then prefer staying (deterministic)
        cand = (-(max_adv), my_nearest, 0 if (dx == 0 and dy == 0) else 1, dx, dy)
        if best is None or cand < best[0]:
            best = (cand, dx, dy)

    return [best[1], best[2]]