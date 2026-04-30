def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs_set = set((x, y) for x, y in obstacles)
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return abs(dx) + abs(dy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Pick best resource based on who is closer, with deterministic tie-breaking.
    best = None
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # Smaller is better. Prefer resources where we're closer; also encourage closer absolute.
        score = (ds - do) * 10 + ds
        # Mildly prefer resources toward our side
        score += (rx - (w - 1) / 2) ** 2 * 1e-3
        cand = (score, ds, do, rx, ry)
        if best is None or cand < best:
            best = cand
    _, _, _, tx, ty = best

    # Choose move that reduces distance to target while avoiding obstacles.
    best_move = (10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue
        nds = dist((nx, ny), (tx, ty))
        # Extra penalty if it also brings us closer to opponent's nearest resource-like position.
        # (Quick proxy: if opponent is adjacent to same cell region, avoid.)
        opp_to = dist((ox, oy), (tx, ty))
        # Deterministic "enemy threat": discourage moves that don't improve and lets opponent keep lead.
        impro = nds - dist((sx, sy), (tx, ty))
        score = nds * 100 + (0 if impro < 0 else 5 * impro) + (opp_to - nds) * 0.1
        tie = (score, dx, dy, nx, ny)
        if tie < best_move:
            best_move = tie

    return [best_move[1], best_move[2]]