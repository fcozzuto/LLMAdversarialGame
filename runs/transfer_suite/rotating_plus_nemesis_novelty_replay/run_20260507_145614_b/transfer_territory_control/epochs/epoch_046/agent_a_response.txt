def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Select a deterministic target: nearest unclaimed where we are relatively closer than opponent.
    if unclaimed:
        best = None
        best_key = None
        for x, y in unclaimed:
            d1 = man(sx, sy, x, y)
            d2 = man(ox, oy, x, y)
            # Prefer taking cells where we are closer; add slight preference for closer to our side.
            k = (d1, -d2, x, y)
            if best_key is None or k < best_key:
                best_key = k
                best = (x, y)
        tx, ty = best
    else:
        # No unclaimed info: move toward opponent's territory cells or center.
        opp = observation.get("opponent_territory") or []
        if opp:
            ox2, oy2 = opp[0][0], opp[0][1]
            for p in opp[1:]:
                x, y = p[0], p[1]
                if man(sx, sy, x, y) < man(sx, sy, ox2, oy2):
                    ox2, oy2 = x, y
            tx, ty = ox2, oy2
        else:
            tx, ty = w // 2, h // 2

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        # Greedy: reduce distance to target; avoid moving away; also avoid getting adjacent to obstacles doesn't matter.
        dist_to_t = man(nx, ny, tx, ty)
        dist_to_o = man(nx, ny, ox, oy)
        # Prefer actions that reduce distance to target first, then increase distance from opponent.
        score = (dist_to_t, -dist_to_o, abs(dx) + abs(dy), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]