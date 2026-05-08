def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = [0, 0]
    best_score = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue

            # If we are already on a resource, take the move that preserves/continues; stay is fine.
            move_score = None
            for tx, ty in res:
                sd = man(nx, ny, tx, ty)
                od = man(ox, oy, tx, ty)
                # Prefer resources we can beat the opponent for; slight tie-break to get earlier/closer.
                beat = sd - od
                # Encourage stepping toward resources while discouraging letting opponent be closer.
                score = beat * 10 + sd
                # Mild bias: don't move into opponent's immediate neighborhood if avoidable.
                score += 2 if man(nx, ny, ox, oy) <= 1 else 0
                # Tie-break deterministically: smaller sd, then lower (tx,ty).
                score += 0.001 * (tx + 0.1 * ty)

                if move_score is None or score < move_score:
                    move_score = score

            if best_score is None or move_score < best_score:
                best_score = move_score
                best_move = [dx, dy]
            elif move_score == best_score:
                # Deterministic tie-break on move ordering preference.
                if (dx, dy) < (best_move[0], best_move[1]):
                    best_move = [dx, dy]

    return best_move