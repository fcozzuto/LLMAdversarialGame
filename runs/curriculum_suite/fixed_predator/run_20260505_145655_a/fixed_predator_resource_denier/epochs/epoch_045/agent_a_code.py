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

    # Pick best next position by deterministic local evaluation.
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate by best resource we can out-approach after this move.
        best_for_us = -10**18
        best_for_denial = -10**18
        for rx, ry in resources:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)

            # Encourage winning races to resources; penalize being far.
            sc = (oppd - selfd) * 6 - selfd
            if sc > best_for_us:
                best_for_us = sc

            # Denial: if opponent is ahead, try to move closer to that same resource.
            # (We don't know exact target, but proximity to their lead resource helps.)
            lead = oppd - selfd
            dc = (selfd * -1) + (lead if lead < 0 else 0) * 3
            if dc > best_for_denial:
                best_for_denial = dc

        # Mix: if we are generally behind, increase denial weight.
        # Compute a quick "overall behind" signal at next position.
        worst_gap = 10**18
        for rx, ry in resources:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)
            gap = selfd - oppd  # positive => behind
            if gap < worst_gap:
                worst_gap = gap

        behind = 1 if worst_gap > 0 else 0
        val = best_for_us * (1 + 0.35 * (1 - behind)) + best_for_denial * (0.9 * behind) - (abs(nx - sx) + abs(ny - sy)) * 0.01

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move