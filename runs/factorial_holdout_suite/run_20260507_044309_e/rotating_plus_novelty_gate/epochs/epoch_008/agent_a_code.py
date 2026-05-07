def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set()
    for p in observation.get("obstacles", []):
        obstacles.add((p[0], p[1]))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    valid_moves = []
    for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid_moves.append((dx, dy, nx, ny))
    if not valid_moves:
        return [0, 0]

    # Precompute opponent distances
    opp_d = {}
    for rx, ry in resources:
        if (rx, ry) not in obstacles:
            opp_d[(rx, ry)] = man(ox, oy, rx, ry)
    if not opp_d:
        return [0, 0]

    # Choose move that maximizes the best "win margin" to any resource,
    # with tie-breaks to avoid deadlocks and prefer earlier, safer progress.
    best = None
    for dx, dy, nx, ny in valid_moves:
        best_margin = -10**9
        best_tie = None
        for (rx, ry), od in opp_d.items():
            sd = man(nx, ny, rx, ry)
            margin = od - sd  # positive => we arrive earlier (or tie if 0)
            # Tie-break: closer resource, prefer moves that move toward it, prefer top-left deterministically.
            # Also slightly penalize moving away from opponent's current line to reduce "denier" traps.
            approach = abs(nx - rx) + abs(ny - ry)
            tie = (margin, -approach, -(abs(nx - ox) + abs(ny - oy)), -(rx + ry))
            if margin > best_margin or (margin == best_margin and (best_tie is None or tie > best_tie)):
                best_margin = margin
                best_tie = tie

        # Secondary move tie-break: prefer moves that reduce distance to the best target.
        # Deterministic ordering by (dx, dy) after score tie.
        if best is None or (best_margin, best_tie) > best[0]:
            best = ((best_margin, best_tie), dx, dy)

    return [best[1], best[2]]