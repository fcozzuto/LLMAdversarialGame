def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = [(r[0], r[1]) for r in (observation.get("resources") or [])]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def min_d2(x, y):
        if not resources:
            return None
        best = None
        for rx, ry in resources:
            d = dist2(x, y, rx, ry)
            if best is None or d < best:
                best = d
        return best

    # If no resources, drift toward center while slightly separating from opponent.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        best_sc = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = -dist2(nx, ny, tx, ty) - 0.1 * dist2(nx, ny, ox, oy)
            if best_sc is None or sc > best_sc or (sc == best_sc and (dx, dy) < best):
                best_sc = sc
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    my_d = min_d2(sx, sy)
    op_d = min_d2(ox, oy)
    best = (0, 0)
    best_sc = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        my_nd = min_d2(nx, ny)
        # Opponent-safe collector heuristic: assume they move to best adjacent cell for their distance-to-resources.
        o_best = None
        o_best_d = None
        for odx, ody in deltas:
            onx, ony = ox + odx, oy + ody
            if not in_bounds(onx, ony) or (onx, ony) in obstacles:
                continue
            d = min_d2(onx, ony)
            if d is None:
                continue
            if o_best_d is None or d < o_best_d or (d == o_best_d and (odx, ody) < o_best):
                o_best_d = d
                o_best = (odx, ody)
        # If no valid opponent move, treat their distance as unchanged.
        next_op_d = o_best_d if o_best_d is not None else op_d

        # Benefit: reduce our distance; Penalty: worsen their distance.
        # Also lightly prefer moves that keep us from being too close to opponent (avoid mutual contest only when it helps us).
        my_gain = (my_d - my_nd) if my_d is not None else 0
        op_loss = (next_op_d - op_d) if op_d is not None else 0
        sep = dist2(nx, ny, ox, oy)
        sc = 3.0 * my_gain - 2.5 * op_loss + 0.01 * sep

        if best_sc is None or sc > best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)

    return [best[0], best[1]]