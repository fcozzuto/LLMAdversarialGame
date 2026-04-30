def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Pick target: resources where opponent is relatively farther (maximize do-ds); tie-break by smaller ds then lex.
    tx = ty = None
    best_val = None
    best_ds = None
    for rx, ry in resources:
        if (rx, ry) in obstacles or (rx, ry) == (ox, oy):
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        val = do - ds
        if best_val is None or val > best_val or (val == best_val and (ds < best_ds or (ds == best_ds and (rx, ry) < (tx, ty)))):
            best_val, best_ds, tx, ty = val, ds, rx, ry

    if tx is None:
        # No useful resources: move to increase distance from opponent while staying within bounds and avoiding obstacles.
        tx, ty = 0, 0
        if (0, 0) == (ox, oy) or (0, 0) in obstacles:
            tx, ty = w - 1, h - 1

    occ_obs = obstacles | {(ox, oy)}
    ds_now = man(sx, sy, tx, ty)
    do_now = man(sx, sy, ox, oy)
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        # Avoid moving onto opponent if possible (still deterministic even if all bad).
        if (nx, ny) == (ox, oy):
            continue
        ds_next = man(nx, ny, tx, ty)
        do_next = man(nx, ny, ox, oy)
        # Score: prioritize getting closer to target, and simultaneously increase our distance from opponent.
        score = (ds_now - ds_next) * 3 + (do_next - do_now) * 2 - (0 if (nx, ny) != (ox, oy) else 1000)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    # If every move was filtered out (rare), allow staying.
    return [int(best_move[0]), int(best_move[1])]