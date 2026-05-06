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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    if not resources:
        return [0, 0]

    best = (0, 0)
    best_val = -10**30
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate by targeting the resource that best balances: approach for us, away for opponent.
        # Denier-style: prefer cells that make our chosen target less attractive to opponent.
        target_val = -10**30
        for rx, ry in resources:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(nx - ox) + abs(ny - oy) + 0  # our move affects opponent only via their distance to target next turn; proxy

            # Better if we are close to the resource while opponent is (likely) far from the same area.
            # Also slightly penalize moves that don't reduce our best achievable distance.
            score = (-2.2 * selfd) + (0.9 * (abs(rx - ox) + abs(ry - oy))) - (1 if (dx == 0 and dy == 0) else 0)
            if score > target_val:
                target_val = score

        # If we can step directly onto a resource, strongly prefer it.
        if (nx, ny) in resources:
            val = 10**12 + target_val
        else:
            # Secondary objective: directly minimize distance to nearest resource.
            nearest = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
            val = target_val - 3.0 * nearest

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]