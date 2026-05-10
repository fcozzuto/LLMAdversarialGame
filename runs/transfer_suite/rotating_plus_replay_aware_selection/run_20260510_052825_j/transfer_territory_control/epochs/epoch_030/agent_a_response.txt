def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]

    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells") or []))
    oppT = set((p[0], p[1]) for p in (observation.get("opponent_territory") or []))

    opp_pos = observation.get("opponent_position", None)
    if opp_pos and isinstance(opp_pos, list) and len(opp_pos) == 2:
        ocx, ocy = opp_pos[0], opp_pos[1]
    elif oppT:
        sx = sy = 0
        n = len(oppT)
        for px, py in oppT:
            sx += px
            sy += py
        ocx, ocy = sx / n, sy / n
    else:
        ocx, ocy = w - 1, h - 1

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def unclaimed_neighbor_count(px, py):
        c = 0
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = px + dx, py + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in unclaimed:
                c += 1
        return c

    best = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            nx, ny = x, y
        base = 0.0

        if (nx, ny) in unclaimed:
            base += 1.2
        if (nx, ny) in oppT:
            base += 2.4  # flip on entry

        base += 0.35 * unclaimed_neighbor_count(nx, ny)

        # Prefer actions that move toward opponent while not being too close to borders/obstacles.
        dist_before = abs(x - ocx) + abs(y - ocy)
        dist_after = abs(nx - ocx) + abs(ny - ocy)
        base += 0.12 * (dist_before - dist_after)

        # Small tie-break toward progress diagonals earlier to avoid "staying" cycles.
        base += 0.01 * (1 if dx != 0 and dy != 0 else 0)

        if best is None or base > best_val:
            best_val = base
            best = [dx, dy]

    return [int(best[0]), int(best[1])]