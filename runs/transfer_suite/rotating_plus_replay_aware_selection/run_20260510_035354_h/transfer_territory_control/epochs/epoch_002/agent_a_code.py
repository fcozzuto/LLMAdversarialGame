def choose_move(observation):
    ax, ay = observation["self_position"]
    bx, by = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        x, y = p
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    uc = observation.get("unclaimed_cells") or []
    targets = []
    for p in uc:
        x, y = p
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            targets.append((x, y))
        if len(targets) >= 30:
            break
    if not targets:
        targets = [(bx, by)]

    attack = (observation.get("turn_index", 0) % 4) >= 2
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_mv = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        md = 10**9
        for tx, ty in targets:
            d = abs(tx - nx) + abs(ty - ny)
            if d < md:
                md = d
        op = abs(bx - nx) + abs(by - ny)
        score = -md - (0.15 * op if attack else 0.0)
        key = (score, -op, ny, nx, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_mv = (dx, dy)

    dx, dy = best_mv
    return [int(dx), int(dy)]