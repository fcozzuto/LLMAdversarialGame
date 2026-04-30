def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obst = set((x, y) for x, y in obstacles)

    def clamp_in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Always consider staying; but filter invalid moves (engine would keep anyway)
    valid_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if clamp_in_bounds(nx, ny) and (nx, ny) not in obst:
            valid_moves.append((dx, dy))
    if not valid_moves:
        return [0, 0]

    # Pick a target resource: prefer resources we are closer to than opponent.
    target = None
    best = -10**18
    for rx, ry in resources:
        ds = max(abs(rx - sx), abs(ry - sy))
        do = max(abs(rx - ox), abs(ry - oy))
        # Higher when we are much closer; break ties toward closer overall.
        score = (do - ds) * 100 - ds
        if score > best:
            best = score
            target = (rx, ry)

    if target is None:
        # No resources: drift toward center while keeping distance from opponent.
        cx, cy = (w - 1) / 2, (h - 1) / 2
        bestm = -10**18
        bestdxdy = (0, 0)
        for dx, dy in valid_moves:
            nx, ny = sx + dx, sy + dy
            dist_center = abs(nx - cx) + abs(ny - cy)
            sep = max(abs(nx - ox), abs(ny - oy))
            score = -dist_center + sep * 0.5
            if score > bestm:
                bestm = score
                bestdxdy = (dx, dy)
        return [bestdxdy[0], bestdxdy[1]]

    tx, ty = target

    # If adjacent to opponent, consider moving to improve separation slightly while going for target.
    adj_opp = max(abs(sx - ox), abs(sy - oy)) <= 1

    bestm = -10**18
    bestdxdy = (0, 0)
    for dx, dy in valid_moves:
        nx, ny = sx + dx, sy + dy
        d_to_t = max(abs(tx - nx), abs(ty - ny))
        d_to_t_now = max(abs(tx - sx), abs(ty - sy))
        # Prefer reaching target; reward decreasing distance.
        progress = d_to_t_now - d_to_t
        # Encourage staying away from opponent to prevent interference.
        sep = max(abs(nx - ox), abs(ny - oy))
        # If adjacent, prioritize separation more.
        sep_weight = 6 if adj_opp else 2
        # Slight preference for capturing (standing on resource) if present.
        on_resource = 1 if (nx, ny) in set((r[0], r[1]) for r in resources) else 0
        score = progress * 50 - d_to_t + sep * sep_weight + on_resource * 200
        if score > bestm:
            bestm = score
            bestdxdy = (dx, dy)

    return [bestdxdy[0], bestdxdy[1]]