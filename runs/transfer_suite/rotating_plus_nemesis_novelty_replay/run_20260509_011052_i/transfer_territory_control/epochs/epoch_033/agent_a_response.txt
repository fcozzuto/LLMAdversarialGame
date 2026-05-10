def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    oxp, oyp = observation.get("opponent_position", (w - 1, h - 1))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed_list = observation.get("unclaimed_cells", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # Anchor: pick a deterministic "frontier" target from unclaimed (prefer far from opponent, close to us)
    if unclaimed_list:
        best_t = None
        best_key = None
        for (x, y) in unclaimed_list:
            x = int(x); y = int(y)
            d1 = abs(x - sx) + abs(y - sy)
            d2 = abs(x - oxp) + abs(y - oyp)
            key = (d1 - 0.35 * d2, y, x)
            if best_key is None or key < best_key:
                best_key = key
                best_t = (x, y)
        tx, ty = best_t
    else:
        # If no unclaimed info, target the opposite side of opponent.
        tx, ty = (0 if oxp > (w - 1) / 2 else w - 1, 0 if oyp > (h - 1) / 2 else h - 1)

    def adj_self(x, y):
        c = 0
        for dx, dy in dirs4:
            if (x + dx, y + dy) in self_terr:
                c += 1
        return c

    def dist_to_target(x, y):
        return abs(x - tx) + abs(y - ty)

    candidates = []
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        in_opp = (nx, ny) in opp_terr
        in_self = (nx, ny) in self_terr
        d_opp = abs(nx - oxp) + abs(ny - oyp)

        # Heuristic:
        # - Huge reward for flipping opponent cells.
        # - Next for taking unclaimed/loosely away from opponent pressure.
        # - Maintain expansion continuity with own frontier.
        # - Avoid stepping into opponent territory if not flipping (handled by huge reward anyway).
        score = 0.0
        if in_opp:
            score += 140.0 + 2.5 * adj_self(nx, ny)
        elif (nx, ny) in self_terr:
            score += 8.0 + 1.5 * adj_self(nx, ny)
        else:
            score += 38.0  # likely unclaimed
            score += 0.8 * adj_self(nx, ny)
            # Prefer being farther from opponent while approaching target
            score += 0.6 * d_opp
        score -= 0.9 * dist_to_target(nx, ny)

        # Small bias to avoid oscillation: prefer staying directionally aligned to target
        score -= 0.02 * (dx + dy) ** 2
        candidates.append((score, ny, nx, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort()
    _, _, _, dx, dy = candidates[0]
    return [int(dx), int(dy)]