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
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    # Deterministic tie-break: fixed order of moves above.
    best_move = (0, 0)
    best_val = -10**18

    # Small deterministic bias to reduce oscillation: prefer moves that move "forward" toward opponent half-plane.
    midx, midy = (sx + ox) / 2.0, (sy + oy) / 2.0
    forward_dx = 1 if ox > sx else (-1 if ox < sx else 0)
    forward_dy = 1 if oy > sy else (-1 if oy < sy else 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Base "intercept" incentive: get closer to contested region between agents.
        inter = -(abs(nx - midx) + abs(ny - midy))

        best_res = -10**18
        for rx, ry in resources:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)

            # Out-approach payoff; also strongly prioritize resources where we're already closer.
            # Penalty if self distance is large.
            val = (oppd - selfd) * 12 - selfd

            # If we're strictly closer to this resource than opponent by margin, add big boost.
            if selfd + 1 < oppd:
                val += 60

            # If opponent is much closer, slightly prefer moves that reduce our gap more.
            if oppd + 2 < selfd:
                val -= (selfd - oppd) * 2

            if val > best_res:
                best_res = val

        # Encourage moving generally toward opponent direction (helps resource denial contest).
        forward = (dx * forward_dx + dy * forward_dy)
        val_total = best_res + inter + forward

        if val_total > best_val:
            best_val = val_total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]