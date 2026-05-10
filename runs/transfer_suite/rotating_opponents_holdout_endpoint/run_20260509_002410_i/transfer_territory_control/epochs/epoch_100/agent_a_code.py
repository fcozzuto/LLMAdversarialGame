def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    selfT = to_set("self_territory")
    oppT = to_set("opponent_territory")
    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    obstacles = to_set("obstacles")

    targets = list(unclaimed)
    if not targets:
        targets = [(ox, oy)]
    # Prefer claiming near opponent while not suiciding into the middle
    tx, ty = min(targets, key=lambda t: (abs(t[0] - ox) + abs(t[1] - oy), -(abs(t[0] - sx) + abs(t[1] - sy))))

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**9
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        base = 0
        if (nx, ny) in unclaimed:
            base += 5
        elif (nx, ny) in oppT:
            base += 4
        elif (nx, ny) in selfT:
            base += 1

        # Push towards target; add mild repulsion from opponent when too close to reduce flips loss-trade
        d_t = abs(nx - tx) + abs(ny - ty)
        d_o = abs(nx - ox) + abs(ny - oy)
        score = base - d_t - (2 if d_o <= 1 else 0)
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]