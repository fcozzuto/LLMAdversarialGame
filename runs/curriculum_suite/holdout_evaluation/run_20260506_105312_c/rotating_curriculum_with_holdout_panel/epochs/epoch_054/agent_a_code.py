def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def manh(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = manh(nx, ny, tx, ty)
            key = (d, nx, ny)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    opp_map = {}
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            d = manh(x, y, ox, oy)
            opp_map[(x, y)] = d

    best_key = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # If we land on a resource, prioritize immediately.
        on_resource = (nx, ny) in opp_map
        best_adv = None
        best_self = None
        for (rx, ry), opp_d in opp_map.items():
            self_d = manh(nx, ny, rx, ry)
            # Advantage: prefer resources that are closer for us and farther for opponent.
            adv = (opp_d - self_d)
            cand = (adv, -self_d)
            if best_adv is None or cand > best_adv:
                best_adv = cand
                best_self = self_d
        # Key to maximize: on_resource first, then advantage, then reduce our distance, tie-break by coordinates.
        # Convert to minimization by negating where needed.
        adv_score = best_adv[0] if best_adv is not None else -10**9
        self_score = best_self if best_self is not None else 10**9
        key = (0 if on_resource else 1, -adv_score, self_score, nx, ny, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]