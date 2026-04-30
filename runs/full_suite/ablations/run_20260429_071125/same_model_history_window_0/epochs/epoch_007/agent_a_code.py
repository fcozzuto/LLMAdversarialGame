def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        # No resources known: move toward opponent slightly to reduce their options (deterministic)
        tx = 1 if ox > sx else (-1 if ox < sx else 0)
        ty = 1 if oy > sy else (-1 if oy < sy else 0)
        nx, ny = sx + tx, sy + ty
        return [tx, ty] if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles else [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    best_score = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d_self = dist((sx, sy), (rx, ry))
        d_opp = dist((ox, oy), (rx, ry))
        # Prefer closer resources; if contested, prefer where we are not far behind
        score = (d_opp - d_self) * 10 - d_self
        if best is None or score > best_score or (score == best_score and (rx, ry) < best):
            best = (rx, ry)
            best_score = score

    tx, ty = best
    if abs(tx - sx) <= 1 and abs(ty - sy) <= 1:
        return [tx - sx, ty - sy]

    target_dx = 0 if tx == sx else (1 if tx > sx else -1)
    target_dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Candidate moves: those that move toward target; otherwise fallback to best among all legal moves.
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    # Primary: moves with maximum reduction in distance to target
    curd = dist((sx, sy), (tx, ty))
    cand = []
    for dx, dy, nx, ny in legal:
        nd = dist((nx, ny), (tx, ty))
        improve = curd - nd
        cand.append((improve, -abs((nx - ox)) - abs((ny - oy)), nd, dx, dy, nx, ny))
    cand.sort(reverse=True)
    _, _, _, dx, dy, _, _ = cand[0]

    # Secondary tie-break: if best move still doesn't reduce distance (rare), prefer toward target direction, else stay
    if dist((sx + dx, sy + dy), (tx, ty)) >= curd:
        preferred = (target_dx, target_dy)
        nx, ny = sx + preferred[0], sy + preferred[1]
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [preferred[0], preferred[1]]
        return [0, 0]
    return [dx, dy]