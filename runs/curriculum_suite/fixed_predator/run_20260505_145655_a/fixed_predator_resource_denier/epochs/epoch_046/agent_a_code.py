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
            x, y = int(r[0]), int(r[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    # Decide target set based on whether we can out-approach some resource.
    scored_cells = []
    for (rx, ry) in resources:
        selfd = abs(sx - rx) + abs(sy - ry)
        oppd = abs(ox - rx) + abs(oy - ry)
        # favor cells where we are closer than opponent (resource_denier)
        sc = (oppd - selfd) * 5 - selfd
        scored_cells.append((sc, selfd, oppd, rx, ry))
    scored_cells.sort(key=lambda t: (-t[0], t[3], t[4]))
    best_sc = scored_cells[0][0]
    if best_sc > 0:
        targets = [(t[3], t[4]) for t in scored_cells[:3]]
    else:
        # contested mode: chase the soonest-opponent resource to avoid getting denied
        contested = min(scored_cells, key=lambda t: (t[2], t[3], t[4]))  # minimal oppd
        targets = [(contested[3], contested[4])]
        # add a second option that is at least not terrible for us
        for t in scored_cells:
            if t[2] == contested[2] and (t[3], t[4]) != (contested[3], contested[4]):
                targets.append((t[3], t[4]))
                break

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        local = -10**18
        for (rx, ry) in targets:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)
            # after-move evaluation: maximize our lead and minimize our distance
            val = (oppd - selfd) * 6 - selfd
            if best_sc <= 0:
                # contested: prioritize reducing our distance even if behind
                val = (oppd - selfd) * 3 - selfd * 2
            if val > local:
                local = val
        if local > best_val:
            best_val = local
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]