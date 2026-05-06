def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    if not resources:
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d_opp = cheb(nx, ny, ox, oy)
            key = (d_opp, dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    best_key = None
    best_move = (0, 0)

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Evaluate this move by the best target we could race to
        best_for_move = None
        for rx, ry in resources:
            d_us = cheb(nx, ny, rx, ry)
            d_them = cheb(ox, oy, rx, ry)
            # Prefer making our distance small and our advantage large
            # advantage = d_them - d_us (bigger is better)
            advantage = d_them - d_us
            # primary: maximize advantage; then minimize our distance; then deterministic tiebreak
            key = (-advantage, d_us, rx, ry)
            if best_for_move is None or key < best_for_move:
                best_for_move = key
        # Secondary tie-breaks: avoid wasting moves, and keep consistent preference
        overall = (best_for_move, cheb(nx, ny, ox, oy), dx, dy)
        if best_key is None or overall < best_key:
            best_key = overall
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]