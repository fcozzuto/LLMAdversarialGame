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

    def cell_block(cell):
        x, y = cell
        s = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                s += 1
        return s

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        my_here = 0
        opp_here = 0
        for rx, ry in resources:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)

            # Main goal: resources we are likely to win (out-approach opponent).
            win_term = (oppd - selfd) * 5 - selfd

            # Denial: if opponent is closer, still consider moves that reduce the gap.
            deny_term = (selfd - oppd) * 2 + selfd * 0

            # Small tie-break for "committing" to good areas.
            local_commit = -(min(selfd, oppd) * 0.15)

            # Prefer resources with nearby obstacle density (tends to stabilize routes).
            block_bias = cell_block((rx, ry)) * 0.3

            val = win_term + deny_term + local_commit + block_bias

            # Extra: if we can be equal/near-equal, favor exact picks deterministically.
            if selfd == oppd:
                val += 2.0
            my_here += val * 0.0
            if val > 0:
                my_here += val

            if oppd < selfd:
                opp_here += (selfd - oppd)

        # Combine:
        # - primary: max over resources (approach win)
        # - secondary: reduce "how much opponent is ahead overall"
        # Deterministic preference: prefer closer-to-center among equals.
        total_best = -10**18
        for rx, ry in resources:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)
            sc = (oppd - selfd) * 5 - selfd
            if selfd == oppd:
                sc += 2.0
            sc += cell_block((rx, ry)) * 0.3
            if sc > total_best:
                total_best = sc

        center = (nx - (w - 1) / 2.0) ** 2 + (ny - (h - 1) / 2.0) ** 2
        val = total_best * 10 - opp_here * 0.5 - center * 0.01

        if val > best_val or (val == best_val and (dx, dy) < tuple(best_move)):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]