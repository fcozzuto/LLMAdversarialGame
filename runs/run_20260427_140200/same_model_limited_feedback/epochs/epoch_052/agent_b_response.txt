def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def clamp_in(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_target():
        if not resources:
            return None
        best = None
        best_adv = -10**9
        for r in resources:
            sd = dist((sx, sy), r)
            od = dist((ox, oy), r)
            adv = od - sd
            if adv > best_adv or (adv == best_adv and (best is None or sd < dist((sx, sy), best))):
                best_adv = adv
                best = r
        return best

    target = best_target()

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if target is None:
        return [0, 0]

    tx, ty = target
    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_in(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        self_to_t = dist((nx, ny), (tx, ty))
        opp_to_t = dist((ox, oy), (tx, ty))
        opp_after = dist((nx, ny), (ox, oy))
        # Prefer reducing distance to chosen target, but also keep away from opponent.
        score = (opp_after * 1.8) + ((opp_to_t - self_to_t) * 2.2) - (self_to_t * 1.1)
        # Small bias toward staying mobile toward target
        if (nx, ny) == (sx, sy):
            score -= 0.25
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]