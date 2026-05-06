def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            t = (int(r[0]), int(r[1]))
            if t not in obstacles:
                resources.append(t)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    best = (None, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        local = -10**18
        for rx, ry in resources:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)

            # Bias toward resources we can win soon; also handle "denier" by
            # explicitly contesting resources where the opponent is currently closer.
            advantage = oppd - selfd  # positive => we are closer to that resource
            sc = advantage * 8 - selfd * 1.2

            # Slight preference for moving away from immediate danger by not
            # collapsing into opponent's exact chase vicinity (helps robustness).
            sc -= 0.08 * (abs(nx - ox) + abs(ny - oy))

            # Encourage not oscillating: prefer fewer steps overall.
            sc -= 0.03 * (abs(nx - sx) + abs(ny - sy))

            if sc > local:
                local = sc

        # Deterministic tie-break: lexicographic by (dx,dy) over move set order.
        if local > best[1]:
            best = ((dx, dy), local)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]