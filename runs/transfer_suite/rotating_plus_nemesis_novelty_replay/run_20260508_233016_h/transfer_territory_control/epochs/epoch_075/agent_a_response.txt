def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Pick a deterministic target set: near our position and near opponent
    if unclaimed:
        def tgt_key(c):
            x, y = c
            d_us = abs(x - sx) + abs(y - sy)
            d_opp = abs(x - ox) + abs(y - oy)
            opp_bias = 0 if (x, y) in oppT else 3
            return (d_us * 2 + d_opp - opp_bias, x, y)
        targets = unclaimed
        targets = sorted(targets, key=tgt_key)[:16]
    else:
        targets = [(ox, oy)]

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Base preference: move into opponent territory strongly, unclaimed moderately
        score = 0
        if (nx, ny) in oppT:
            score += 1200
        elif (nx, ny) in selfT:
            score += 10
        else:
            score += 120 if (nx, ny) in set(map(tuple, unclaimed)) else 80

        # Additional pressure: reduce distance to some good target
        if targets:
            dmin = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
            score += 25 * (-dmin)

        # Mild anti-jitter: prefer moves that keep parity consistent (deterministic)
        score += -(abs(dx) + abs(dy)) * 0.2

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]