def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    w = observation["grid_width"]
    h = observation["grid_height"]

    if not resources:
        return [0, 0]

    def best_target():
        best = None
        best_key = None
        for x, y in resources:
            sd = abs(x - sx) + abs(y - sy)
            od = abs(x - ox) + abs(y - oy)
            # Prefer resources we can reach sooner; break ties by farther-from-opponent and closeness.
            key = (-(od - sd), sd, x, y)  # minimal key
            if best_key is None or key < best_key:
                best_key = key
                best = (x, y, sd, od)
        return best

    tx, ty, sd, od = best_target()

    # Local obstacle-aware move toward target.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, abs(tx - nx) + abs(ty - ny)))
    if not moves:
        return [0, 0]

    # If opponent is about to beat us, prioritize a "steal" by choosing move that maximizes our reach advantage after step.
    if od <= sd:
        best = None
        best_key = None
        for dx, dy, _ in moves:
            nx, ny = sx + dx, sy + dy
            n_sd = abs(tx - nx) + abs(ty - ny)
            n_od = abs(tx - ox) + abs(ty - oy)
            # maximize advantage; then reduce distance.
            key = (-(n_od - n_sd), n_sd, nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    moves.sort(key=lambda t: (t[2], t[0], t[1]))
    dx, dy, _ = moves[0]
    return [int(dx), int(dy)]