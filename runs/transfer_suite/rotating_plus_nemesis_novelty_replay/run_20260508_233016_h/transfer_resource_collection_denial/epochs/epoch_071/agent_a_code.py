def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        my_d = dist(sx, sy, rx, ry)
        op_d = dist(ox, oy, rx, ry)
        diff = op_d - my_d  # positive means we arrive earlier
        secure = 1 if diff > 0 else 0
        risk = 0 if secure else (0 - diff)  # smaller is better
        # Encourage closer secure targets; if none secure, delay by choosing where opponent is far or where we are least behind.
        key = (0 if secure else 1, risk, my_d, op_d, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry), my_d, op_d)
    (tx, ty) = best[1]

    # If we can secure something now, bias toward moves that keep improving our lead toward that target.
    # If not, also consider "deny" by moving toward a resource that reduces opponent's advantage next step.
    my_d0 = dist(sx, sy, tx, ty)
    op_d0 = dist(ox, oy, tx, ty)

    best_move = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_d = dist(nx, ny, tx, ty)
        op_d = dist(ox, oy, tx, ty)  # opponent not moved this turn
        lead = op_d - my_d
        lead_improve = (op_d0 - my_d0) - lead  # negative if lead gets better
        # Also include a small "reach-now" component to prevent dithering.
        reach_key = my_d
        # Deny/transition: if we're behind, slightly prefer moves that increase lead (reduce opponent's chances).
        # Deterministic tie-break uses (dx,dy).
        key = (0 if best[0][0] == 0 else 1, -lead, reach_key, lead_improve, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]