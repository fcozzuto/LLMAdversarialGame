def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)

    self_t = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) == 2)
    opp_t = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) == 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) == 2)
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if p and len(p) == 2)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def d1(x, y, tx, ty): return abs(tx - x) + abs(ty - y)

    # Targets: prioritize nearest unclaimed; if none, push towards opponent territory; else center.
    if unclaimed:
        txu, tyu = min(unclaimed, key=lambda t: (d1(sx, sy, t[0], t[1]), (t[0] - sx) ** 2 + (t[1] - sy) ** 2))
    elif opp_t:
        txu, tyu = min(opp_t, key=lambda t: (d1(sx, sy, t[0], t[1]), (t[0] - sx) ** 2 + (t[1] - sy) ** 2))
    else:
        txu, tyu = (int(cx), int(cy))

    if opp_t:
        txo, tyo = min(opp_t, key=lambda t: (d1(sx, sy, t[0], t[1]), (t[0] - sx) ** 2 + (t[1] - sy) ** 2))
    else:
        txo, tyo = (int(cx), int(cy))

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Value of the cell we would occupy/claim this turn.
        if (nx, ny) in self_t:
            v = 0
        elif (nx, ny) in unclaimed:
            v = 3
        elif (nx, ny) in opp_t:
            v = 4  # flipping enemy control
        else:
            v = 1  # edge cases: treat unknown as potentially neutral

        # Strategic pressure: expand towards unclaimed while also counterclaiming nearby enemy.
        score = 0
        score += 120 * v
        score += -7 * d1(nx, ny, txu, tyu)
        score += -4 * d1(nx, ny, txo, tyo)
        # Mild centering to break ties and keep pressure mid-map.
        score += -2 * (abs(nx - cx) + abs(ny - cy))

        # Deterministic tie-break: first encountered in dirs order.
        if score > best[0]:
            best = (score, dx, dy)

    # If all moves invalid (shouldn't happen), stay.
    if best[1] == 0 and best[2] == 0 and (sx, sy) in obstacles:
        return [0, 0]
    return [int(best[1]), int(best[2])]