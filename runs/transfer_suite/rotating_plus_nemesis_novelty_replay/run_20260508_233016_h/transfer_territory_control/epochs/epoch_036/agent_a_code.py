def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    oppx, oppy = observation["opponent_position"]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    best_score = -10**18

    # Precompute nearest-unclaimed distance from current position (manhattan), if any.
    if unclaimed:
        md0 = min(abs(x - sx) + abs(y - sy) for (x, y) in unclaimed if inb(x, y) and (x, y) not in obstacles)
    else:
        md0 = 10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Avoid stepping into opponent territory unless it directly helps capturing unclaimed.
        near_opp = abs(nx - oppx) + abs(ny - oppy)
        is_unclaimed = (nx, ny) in unclaimed
        is_bad = (nx, ny) in opp_terr

        if unclaimed:
            md = min(abs(x - nx) + abs(y - ny) for (x, y) in unclaimed if inb(x, y) and (x, y) not in obstacles)
        else:
            md = md0

        score = 0
        if is_unclaimed:
            score += 2000
        score += 50 * (md0 - md)  # move toward closer unclaimed
        score += 5 * (w + h - near_opp)  # prefer farther from opponent overall
        if is_bad:
            score -= 800 if not is_unclaimed else 200

        # Small deterministic tie-breaker: prefer lexicographically smaller moves.
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]