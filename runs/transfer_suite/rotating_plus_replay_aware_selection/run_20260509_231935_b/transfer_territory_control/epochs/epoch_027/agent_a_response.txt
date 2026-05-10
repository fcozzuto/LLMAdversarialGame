def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obs_cells = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    self_set = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_set = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs_cells:
            continue

        cell_self = (nx, ny) in self_set
        cell_opp = (nx, ny) in opp_set
        cell_un = (nx, ny) in set(unclaimed) if unclaimed else False

        score = 0.0
        if cell_self:
            score += 0.8
        if cell_un:
            score += 3.0
        if cell_opp:
            score += 6.0

        # Encourage moving toward "frontier": unclaimed near our territory, else near opponent.
        targets = None
        if unclaimed:
            targets = unclaimed
        elif opp_set:
            targets = list(opp_set)
        else:
            targets = list(self_set)

        # Small local preference: proximity to nearest target (Manhattan).
        best = 10**9
        tx_ty = None
        for tx, ty in targets:
            d = abs(tx - nx) + abs(ty - ny)
            if d < best:
                best = d
                tx_ty = (tx, ty)
        score += 2.0 / (1.0 + best)

        # Penalize stepping away from our current territory if unclaimed are absent.
        if not unclaimed and self_set:
            best_self = 10**9
            for tx, ty in self_set:
                d = abs(tx - nx) + abs(ty - ny)
                if d < best_self:
                    best_self = d
            score -= 0.4 * best_self

        # Tie-break deterministically toward not staying still on even turns (avoid dithering).
        if (dx, dy) == (0, 0):
            score -= 0.05 if (observation.get("turn_index", 0) % 2 == 0) else 0.0

        moves.append(((score), dx, dy))

    if not moves:
        return [0, 0]

    # Sort by score desc, then deterministic tie-break on dx,dy.
    moves.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(moves[0][1]), int(moves[0][2])]