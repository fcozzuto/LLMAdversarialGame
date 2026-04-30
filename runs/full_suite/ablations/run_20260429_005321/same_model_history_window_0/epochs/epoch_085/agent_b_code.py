def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    cand = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cand.append((dx, dy, nx, ny))

    if not cand:
        return [0, 0]

    if not resources:
        # No resources known: move toward opponent corner as a fallback
        tx, ty = (w - 1, h - 1) if (sx, sy) != (w - 1, h - 1) else (0, 0)
        best = None
        bestv = None
        for dx, dy, nx, ny in cand:
            d = abs(nx - tx) + abs(ny - ty)
            v = (-d, dx, dy)
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Evaluate each move by how much closer we are to resources than the opponent
    # with an extra bias to reduce our nearest distance.
    best_move = (0, 0)
    best_key = None
    for dx, dy, nx, ny in cand:
        # Prefer resource where (opp dist - our dist) is largest; then our distance smallest.
        best_adv = None
        best_d = None
        for rx, ry in resources:
            ds = abs(nx - rx) + abs(ny - ry)
            do = abs(ox - rx) + abs(oy - ry)
            adv = do - ds
            if best_adv is None or adv > best_adv or (adv == best_adv and ds < best_d):
                best_adv = adv
                best_d = ds
        # Tie-break deterministically with a small directional preference (toward increasing x then y)
        key = (best_adv, -best_d, -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]