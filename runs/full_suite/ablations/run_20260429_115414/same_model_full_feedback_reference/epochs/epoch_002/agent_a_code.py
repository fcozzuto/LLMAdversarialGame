def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Targeting change: pick a resource where we are closer than opponent,
    # otherwise fall back to a resource that maximizes (opp_dist - my_dist).
    tx, ty = ox, oy
    best_key = None
    for rx, ry in resources:
        my = d2(sx, sy, rx, ry)
        op = d2(ox, oy, rx, ry)
        # prefer being strictly closer; then minimize our distance; then deterministic tie-break
        key = (1 if my <= op else 0, op - my, -my, rx, ry)
        # Higher advantage (op-my) and being closer => larger key; but tuple compares lexicographically.
        # We'll use inverted for first component: prefer key[0]==1. So maximize key[1], minimize my.
        score = (0 if my <= op else 1, - (op - my), my, rx, ry)
        if best_key is None or score < best_key:
            best_key = score
            tx, ty = rx, ry

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None  # (score, dx, dy)

    # Opponent-aware potential field: chase target, keep distance from opponent, avoid walls/obstacles.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        my_to_t = d2(nx, ny, tx, ty)
        my_to_o = d2(nx, ny, ox, oy)

        # If we can step onto/adjacent to target, heavily prioritize.
        on_target = 1 if (nx, ny) == (tx, ty) else 0

        # Encourage staying between opponent and target by preferring moves that increase distance to opponent.
        score = (
            (0 if on_target else 1),
            my_to_t,
            -(my_to_o),
            (dx == 0 and dy == 0),
            nx, ny
        )

        # Deterministic best: lexicographic minimum with our constructed ordering.
        if best is None or score < best[0]:
            best = (score, dx, dy)

    # Safety fallback: stay put if somehow all moves blocked.
    if best is None:
        return [0, 0]
    return [best[1], best[2]]